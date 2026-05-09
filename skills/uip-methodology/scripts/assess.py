#!/usr/bin/env python3
"""
Assess document coverage for a project directory against the methodology schema.

For each topic in the schema, scans the project artefact files and reports:
  covered     — content found; substantial and specific
  partial     — content found but thin, vague, template-like, or placeholder
  unknown     — owning artefact file absent or topic not found
  conflicting — same topic found in two files with contradictory numeric values

Topics with a review_prompt in the schema are evaluated by an LLM (Anthropic API)
which returns a quality tier: good / medium / low. The LLM tier overrides the
keyword-density status for those topics.

Config resolution order (highest → lowest priority):
  1. CLI argument
  2. Environment variable  (IA_PROJECT, IA_SCHEMA, IA_OUTPUT, IA_MIN_LENGTH,
                            IA_FORMAT, IA_NO_LLM, IA_LLM_MODEL)
  3. Config file           (.interview-guide.yaml in project dir, then repo root)
  4. Opinionated default

Usage:
    uv run --with pyyaml --with anthropic python .claude/skills/uipath-rpa-design/scripts/assess.py \\
        --project docs

    # Skip LLM evaluation:
    uv run --with pyyaml --with anthropic python ... --no-llm

    # JSON to stdout:
    uv run ... --project docs --format json --output -

    # .interview-guide.yaml keys: schema, output, min_answer_length, format,
    #   file_map: {pdd: "*pdd*", sdd: "*sdd*", ...}

Environment variables:
    ANTHROPIC_API_KEY   Required for LLM evaluation (topics with review_prompt)
    IA_NO_LLM           Set to 1 to disable LLM calls
    IA_LLM_MODEL        Override model  (default: claude-haiku-4-5-20251001)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ruamel.yaml import YAML as _YAML

_HERE = Path(__file__).parent  # scripts/
__all__ = [
    "ArtefactFile",
    "Config",
    "CoverageResult",
    "CoverageRow",
    "JsonAdapter",
    "MarkdownAdapter",
    "assess_coverage",
    "build_coverage_map",
    "build_artefact_map",
    "check_conflict",
    "extract_topic_section",
    "get_adapter",
    "keywords",
    "llm_rate_section",
    "main",
]

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_FILE_NAME = ".interview-guide.yaml"
DEFAULT_LLM_MODEL = "claude-haiku-4-5-20251001"

DEFAULT_FILE_MAP: dict[str, str] = {
    "pdd": "*pdd*",
    "arch_chapter": "*arch*",
    "estimation": "*estimat*",
    "roi": "*roi*",
    "sdd": "*sdd*",
    "tdd": "*tdd*",
    "dsd": "*dsd*",
    "glossary": "*glossary*",
    "coverage_map": "*coverage-map*",
    "project_plan": "*plan*",
    "domain_model": "*domain-model*",
}

DEFAULTS: dict = {
    "project": str(_HERE.parent / "testcorpus"),
    "schema": str(_HERE.parent / "references" / "rpa-methodology.yaml"),
    "output": None,
    "min_answer_length": 25,
    "vagueness_limit": 2,
    "format": "markdown",
    "file_map": DEFAULT_FILE_MAP,
    "llm": True,
    "llm_model": DEFAULT_LLM_MODEL,
}

ENV_MAP = {
    "IA_PROJECT": "project",
    "IA_SCHEMA": "schema",
    "IA_OUTPUT": "output",
    "IA_MIN_LENGTH": "min_answer_length",
    "IA_FORMAT": "format",
    "IA_LLM_MODEL": "llm_model",
}

VAGUE_WORDS = re.compile(
    r"\b(various|several|some|tbd|n/?a|as needed|to be (confirmed|defined|agreed)"
    r"|appropriate|relevant|suitable|etc\.?|placeholder|insert here)\b",
    re.I,
)
TEMPLATE_ECHO = re.compile(
    r"^e\.g\.|^example:|^\[insert|^your \w|^add here|^fill in|^describe",
    re.I | re.MULTILINE,
)
PLACEHOLDER = re.compile(
    r"\[TBD\]|\[TODO\]|\[SME REVIEW\]|\[DEFAULT\]"
    r"|\[Name\]|\[YYYY-MM-DD\]|\[Project Name\]|\[Describe|placeholder",
    re.I,
)


@dataclass
class Config:
    project: Path
    schema: Path
    output: Path
    min_answer_length: int
    vagueness_limit: int
    format: str
    file_map: dict[str, str]
    llm: bool
    llm_model: str

    @classmethod
    def resolve(cls, cli: argparse.Namespace) -> "Config":
        cfg: dict = {**DEFAULTS, "file_map": dict(DEFAULT_FILE_MAP)}

        # 3. Config file (project dir first, then cwd)
        for search_dir in [Path(cli.project or "."), Path(".")]:
            cf = search_dir / CONFIG_FILE_NAME
            if cf.exists():
                loaded = _YAML(typ="safe").load(cf.read_text(encoding="utf-8")) or {}
                for k, v in loaded.items():
                    if k == "file_map" and isinstance(v, dict):
                        cfg["file_map"].update(v)
                    elif k in cfg:
                        cfg[k] = v
                break

        # 2. Environment variables
        for env_key, cfg_key in ENV_MAP.items():
            val = os.environ.get(env_key)
            if val is not None:
                cfg[cfg_key] = int(val) if cfg_key == "min_answer_length" else val
        if os.environ.get("IA_NO_LLM", "").strip() == "1":
            cfg["llm"] = False

        # 1. CLI arguments (highest priority)
        if cli.project:
            cfg["project"] = cli.project
        if cli.schema:
            cfg["schema"] = cli.schema
        if cli.output:
            cfg["output"] = cli.output
        if getattr(cli, "format", None):
            cfg["format"] = cli.format
        if getattr(cli, "no_llm", False):
            cfg["llm"] = False
        if getattr(cli, "llm_model", None):
            cfg["llm_model"] = cli.llm_model

        project = Path(cfg["project"])
        fmt = cfg["format"]
        raw_output = cfg["output"]
        if raw_output == "-":
            output = Path("-")
        elif raw_output:
            output = Path(raw_output)
        else:
            output = project / f"coverage-map.{'json' if fmt == 'json' else 'md'}"

        return cls(
            project=project,
            schema=Path(cfg["schema"]),
            output=output,
            min_answer_length=int(cfg["min_answer_length"]),
            vagueness_limit=int(cfg["vagueness_limit"]),
            format=fmt,
            file_map=cfg["file_map"],
            llm=bool(cfg["llm"]),
            llm_model=cfg["llm_model"],
        )


# ---------------------------------------------------------------------------
# Artefact file map
# ---------------------------------------------------------------------------


@dataclass
class ArtefactFile:
    artefact_id: str
    path: Path | None
    headings: list[str] = field(default_factory=list)


def build_artefact_map(project_dir: Path, file_map: dict[str, str]) -> dict[str, "ArtefactFile"]:
    result: dict[str, ArtefactFile] = {}
    for aid, pattern in file_map.items():
        glob = pattern if pattern.endswith(".md") else f"{pattern}.md"
        matches = sorted(project_dir.glob(glob))
        if matches:
            path = matches[0]
            headings = re.findall(r"^#{1,3} .+", path.read_text(encoding="utf-8"), re.MULTILINE)
        else:
            path, headings = None, []
        result[aid] = ArtefactFile(aid, path, headings)
    return result


# ---------------------------------------------------------------------------
# Keywords / qualitative signals
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "is",
    "in",
    "of",
    "to",
    "for",
    "this",
    "that",
    "it",
    "its",
    "with",
    "at",
    "by",
    "from",
    "as",
    "are",
    "was",
    "be",
    "been",
    "do",
    "does",
    "what",
    "which",
    "who",
    "how",
    "when",
    "where",
    "any",
    "all",
    "each",
    "every",
    "me",
    "i",
    "you",
    "we",
    "they",
    "has",
    "have",
    "had",
    "on",
    "if",
    "so",
}


def keywords(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]{3,}", text.lower()) if w not in STOPWORDS]


def qualitative_issues(region: str, cfg: Config) -> list[str]:
    issues = []
    stripped = re.sub(r"\s+", " ", region).strip()
    if len(stripped) < cfg.min_answer_length:
        issues.append("too-short")
    if PLACEHOLDER.search(region):
        issues.append("placeholder")
    if TEMPLATE_ECHO.search(region):
        issues.append("template-echo")
    n_vague = len(VAGUE_WORDS.findall(region))
    if n_vague > cfg.vagueness_limit:
        issues.append(f"vague({n_vague})")
    caps = len(re.findall(r"\b[A-Z][a-zA-Z]{2,}\b", region))
    nums = len(re.findall(r"\b\d[\d,\.]*\b", region))
    if caps + nums < 2 and len(stripped) < 80:
        issues.append("low-specificity")
    return issues


# ---------------------------------------------------------------------------
# Coverage detection
# ---------------------------------------------------------------------------

WINDOW = 350


def find_best_region(topic_kw: list[str], question_kw: list[str], content: str) -> tuple[str, int]:
    combined = list(dict.fromkeys(topic_kw + question_kw))
    lower = content.lower()
    positions = sorted(m.start() for kw in combined for m in re.finditer(re.escape(kw), lower))

    best_region, best_count = "", 0
    i = 0
    while i < len(positions):
        j = i + 1
        while j < len(positions) and positions[j] - positions[i] <= WINDOW:
            j += 1
        if (j - i) > best_count:
            best_count = j - i
            best_region = content[max(0, positions[i] - 30) : min(len(content), positions[i] + WINDOW)]
        i = j
    return best_region, best_count


def assess_coverage(topic_kw: list[str], question_kw: list[str], content: str, cfg: Config) -> tuple[str, list[str]]:
    region, cluster = find_best_region(topic_kw, question_kw, content)
    if cluster < 2:
        return "unknown", []
    issues = qualitative_issues(region, cfg)
    return ("partial", issues) if issues else ("covered", [])


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------


def check_conflict(topic_kw: list[str], file_contents: dict[str, str]) -> bool:
    per_file: dict[str, set[str]] = {}
    for name, content in file_contents.items():
        if any(kw in content.lower() for kw in topic_kw):
            nums = set(re.findall(r"\b\d[\d,\.]*\b", content))
            if nums:
                per_file[name] = nums
    if len(per_file) < 2:
        return False
    vals = list(per_file.values())
    return vals[0].isdisjoint(vals[1])


# ---------------------------------------------------------------------------
# LLM section extraction and evaluation
# ---------------------------------------------------------------------------

SECTION_CAP = 2000  # max chars sent to LLM per section


def extract_topic_section(content: str, topic: str, question: str = "") -> str:
    """Return the markdown section most relevant to topic+question (up to SECTION_CAP chars)."""
    combined_kw = set(keywords(topic)) | set(keywords(question))
    parts = re.split(r"\n(?=#{1,4} )", content)

    best, best_score = "", 0.0
    for part in parts:
        m = re.match(r"^(#{1,4} .+)", part)
        if not m:
            continue
        heading = m.group(1).lower()
        score = float(sum(1 for kw in combined_kw if kw in heading))
        score += sum(0.1 for kw in combined_kw if kw in part.lower())
        if score > best_score:
            best_score, best = score, part

    return (best if best_score > 0 else content)[:SECTION_CAP]


def llm_rate_section(section_text: str, review_prompt: str, model: str = DEFAULT_LLM_MODEL) -> tuple[str, str]:
    """
    Call Anthropic API with review_prompt as rubric.
    Returns (tier: 'low'|'medium'|'good', reason: str).
    Raises ImportError if anthropic package missing, or anthropic.APIError on failure.
    """
    try:
        import anthropic
    except ImportError as err:
        raise ImportError("anthropic package not available — add to run command: --with anthropic") from err

    client = anthropic.Anthropic()
    system = (
        "You are a quality reviewer for RPA project documentation. "
        "You receive a document section and a review rubric. "
        "Respond with exactly one line: TIER | reason "
        "where TIER is exactly one of: low, medium, good. "
        "Keep the reason under 15 words. "
        "Example: medium | Rotation policy is TBD; all other dimensions complete."
    )
    message = client.messages.create(
        model=model,
        max_tokens=80,
        system=system,
        messages=[
            {
                "role": "user",
                "content": f"Review rubric:\n{review_prompt}\n\nDocument section:\n{section_text}",
            }
        ],
    )
    raw = message.content[0].text.strip()
    if "|" in raw:
        tier, reason = raw.split("|", 1)
        tier = tier.strip().lower()
        if tier in ("low", "medium", "good"):
            return tier, reason.strip()
    for t in ("good", "medium", "low"):
        if t in raw.lower():
            return t, raw
    return "medium", raw  # safe fallback


TIER_TO_STATUS = {"good": "covered", "medium": "partial", "low": "partial"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CoverageRow:
    topic: str
    status: str
    issues: list[str]
    source: str
    confidence: str
    quality: str = "—"  # LLM tier: good / medium / low, or — if not evaluated
    quality_reason: str = ""  # one-sentence LLM reason


@dataclass
class CoverageResult:
    rows: list[CoverageRow]
    files: dict[str, ArtefactFile]
    cfg: Config


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build_coverage_map(cfg: Config) -> CoverageResult:
    schema = _YAML(typ="safe").load(cfg.schema.read_text(encoding="utf-8"))
    files = build_artefact_map(cfg.project, cfg.file_map)
    contents = {aid: af.path.read_text(encoding="utf-8") for aid, af in files.items() if af.path}

    api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if cfg.llm and not api_key_present:
        print("[LLM] ANTHROPIC_API_KEY not set — LLM evaluation disabled.", file=sys.stderr)

    rows: list[CoverageRow] = []
    for entry in schema["topics"]:
        topic = entry["topic"]
        question = entry.get("acquisition", {}).get("interview", {}).get("question", "")
        review_prompt = entry.get("purpose", {}).get("review")
        t_kw = keywords(topic)
        q_kw = keywords(question)

        owner_ids = [a["id"] for a in schema["artefacts"] if entry.get("artefacts", {}).get(a["id"], {}).get("owns")]

        if not owner_ids:
            rows.append(CoverageRow(topic, "unknown", [], "—", "—"))
            continue

        statuses, sources, all_issues = [], [], []
        for oid in owner_ids:
            af = files.get(oid)
            if not af or not af.path:
                statuses.append("unknown")
                sources.append("—")
                continue
            status, issues = assess_coverage(t_kw, q_kw, contents[oid], cfg)
            statuses.append(status)
            sources.append(af.path.name)
            all_issues.extend(issues)

        relevant = {oid: contents[oid] for oid in owner_ids if oid in contents}
        if len(relevant) >= 2 and check_conflict(t_kw, relevant):
            final_status = "conflicting"
        elif "covered" in statuses:
            final_status = "covered"
        elif "partial" in statuses:
            final_status = "partial"
        else:
            final_status = "unknown"

        src_name = " + ".join(s for s in sources if s != "—") or "—"
        confidence = "—"
        if final_status in ("covered", "partial") and src_name != "—":
            first_af = next((files[oid] for oid in owner_ids if files.get(oid) and files[oid].path), None)
            if first_af:
                confidence = "low" if "draft" in first_af.path.name.lower() else "high"

        # LLM quality evaluation (only for topics with review_prompt)
        quality, quality_reason = "—", ""
        if review_prompt and cfg.llm and api_key_present and final_status != "unknown":
            for oid in owner_ids:
                if oid not in contents:
                    continue
                section = extract_topic_section(contents[oid], topic, question)
                try:
                    quality, quality_reason = llm_rate_section(section, review_prompt, cfg.llm_model)
                    final_status = TIER_TO_STATUS[quality]
                except Exception as exc:
                    print(f"[LLM] {topic}: {exc}", file=sys.stderr)
                break  # evaluate against first owning artefact with content

        rows.append(
            CoverageRow(
                topic,
                final_status,
                sorted(set(all_issues)),
                src_name,
                confidence,
                quality,
                quality_reason,
            )
        )

    return CoverageResult(rows, files, cfg)


# ---------------------------------------------------------------------------
# Output adapters
# ---------------------------------------------------------------------------

STATUS_ICON = {"covered": "✓", "partial": "~", "unknown": "✗", "conflicting": "!"}


@dataclass
class MarkdownAdapter:
    def render(self, result: CoverageResult) -> str:
        cfg = result.cfg
        lines = [
            "# Coverage Map\n",
            f"Schema: `{cfg.schema}`  |  Project: `{cfg.project}`\n",
            "## Files\n",
            "| Artefact | File | Sections |",
            "| --- | --- | --- |",
        ]
        for aid, af in result.files.items():
            fname = af.path.name if af.path else "—"
            secs = ("; ".join(af.headings[:4]) + ("…" if len(af.headings) > 4 else "")) if af.headings else "—"
            lines.append(f"| {aid} | {fname} | {secs} |")

        has_quality = any(r.quality != "—" for r in result.rows)
        header = "| Topic | Status | Issues | Source | Confidence |"
        divider = "| --- | --- | --- | --- | --- |"
        if has_quality:
            header += " Quality |"
            divider += " --- |"

        lines += ["", "## Coverage\n", header, divider]

        for r in result.rows:
            icon = STATUS_ICON.get(r.status, "")
            issues = ", ".join(r.issues) if r.issues else "—"
            row = f"| {r.topic} | {icon} {r.status} | {issues} | {r.source} | {r.confidence} |"
            if has_quality:
                q_cell = r.quality
                if r.quality_reason:
                    q_cell += f" — {r.quality_reason}"
                row += f" {q_cell} |"
            lines.append(row)

        counts = {
            s: sum(1 for r in result.rows if r.status == s) for s in ("covered", "partial", "unknown", "conflicting")
        }
        lines += [
            "",
            f"**{counts['covered']} covered · {counts['partial']} partial · "
            f"{counts['unknown']} unknown · {counts['conflicting']} conflicting**",
        ]
        return "\n".join(lines)


@dataclass
class JsonAdapter:
    def render(self, result: CoverageResult) -> str:
        cfg = result.cfg
        data = {
            "schema": str(cfg.schema),
            "project": str(cfg.project),
            "files": {
                aid: {"path": str(af.path) if af.path else None, "headings": af.headings}
                for aid, af in result.files.items()
            },
            "rows": [asdict(r) for r in result.rows],
            "summary": {
                s: sum(1 for r in result.rows if r.status == s)
                for s in ("covered", "partial", "unknown", "conflicting")
            },
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


def get_adapter(fmt: str) -> MarkdownAdapter | JsonAdapter:
    return JsonAdapter() if fmt == "json" else MarkdownAdapter()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build artefact coverage map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project", default=None, help="Project directory  [env: IA_PROJECT]")
    parser.add_argument("--schema", default=None, help="rpa-methodology.yaml path  [env: IA_SCHEMA]")
    parser.add_argument("--output", default=None, help="Output path; '-' for stdout only  [env: IA_OUTPUT]")
    parser.add_argument(
        "--format",
        default=None,
        choices=["markdown", "json"],
        help="Output format  [env: IA_FORMAT]",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        default=False,
        help="Disable LLM evaluation even for topics with review_prompt  [env: IA_NO_LLM=1]",
    )
    parser.add_argument(
        "--llm-model",
        default=None,
        help=f"Anthropic model for LLM evaluation  [env: IA_LLM_MODEL, default: {DEFAULT_LLM_MODEL}]",
    )
    cli = parser.parse_args()
    cfg = Config.resolve(cli)

    if not cfg.project.is_dir():
        sys.exit(f"Project directory not found: {cfg.project}")
    if not cfg.schema.exists():
        sys.exit(f"Schema not found: {cfg.schema}")

    result = build_coverage_map(cfg)
    adapter = get_adapter(cfg.format)
    text = adapter.render(result)

    stdout_only = str(cfg.output) == "-"
    if not stdout_only:
        cfg.output.write_text(text, encoding="utf-8")

    # Reconfigure stdout for UTF-8 on Windows (avoids CP1252 UnicodeEncodeError)
    import io

    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print(text)
    if not stdout_only:
        print(f"\nWritten to {cfg.output}")


if __name__ == "__main__":
    main()
