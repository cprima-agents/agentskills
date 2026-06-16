#!/usr/bin/env python3
"""Check consistency across the methodology YAML, templates, and generated docs.

Mode a — skill repo:
    uv run scripts/check_coverage.py templates
    Checks that every snippet referenced in YAML exists on disk, every
    <!-- #region X --> in a template is backed by a snippet or a YAML field,
    and no snippet files are orphaned.

Mode b — project docs directory:
    uv run scripts/check_coverage.py docs [docs-dir]
    Finds artefact files via their file_glob and checks that required
    <!-- #region X --> markers are present in each document.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

# Allow running directly: python scripts/check_alignment.py
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import typer  # noqa: E402
from ruamel.yaml import YAML as _YAML  # noqa: E402

_SKILL_ROOT = _SCRIPTS_DIR.parent  # uipath-rpa-design/
_TEMPLATES_DIR = _SKILL_ROOT / "assets" / "templates"
_SNIPPETS_DIR = _TEMPLATES_DIR / "snippets"
_DEFAULT_SCHEMA = _SKILL_ROOT / "references" / "rpa-methodology.yaml"

_REGION_RE = re.compile(r"<!--\s*#region\s+(\w+)\s*-->")

app = typer.Typer(
    help="Check that methodology YAML, snippet files, and template regions are consistent.",
    no_args_is_help=True,
)
__all__ = ["app", "docs", "templates"]

# ── result levels ─────────────────────────────────────────────────────────────

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

_ICONS = {PASS: "ok", WARN: "!!", FAIL: "XX"}


class _Report:
    def __init__(self) -> None:
        self.total = 0
        self.failures = 0
        self.warnings = 0

    def record(self, level: str, location: str, message: str) -> None:
        self.total += 1
        icon = _ICONS.get(level, "?")
        typer.echo(f"  [{level}] {icon} {location}: {message}")
        if level == FAIL:
            self.failures += 1
        elif level == WARN:
            self.warnings += 1

    def summary(self) -> None:
        typer.echo()
        status = "OK" if self.failures == 0 else "FAILED"
        typer.echo(f"  {self.total} checks -- {self.failures} failed, {self.warnings} warnings  [{status}]")

    @property
    def exit_code(self) -> int:
        return 1 if self.failures else 0


# ── YAML helpers ──────────────────────────────────────────────────────────────


def _load_schema(schema_path: Path) -> dict[str, Any]:
    return _YAML(typ="safe").load(schema_path.read_text(encoding="utf-8"))  # type: ignore[return-value]


def _regions_in_file(path: Path) -> list[str]:
    return _REGION_RE.findall(path.read_text(encoding="utf-8"))


def _known_region_names(schema: dict) -> set[str]:
    """All region names that are backed by YAML: concept model fields + lifecycle regions."""
    names: set[str] = set()
    for topic in schema.get("topics", []):
        for fname in topic.get("concept", {}).get("model", {}).keys():
            names.add(fname)
    for group in schema.get("shared", []):
        for fname in group.get("model", {}).keys():
            names.add(fname)
    lm = schema.get("lifecycle_model", {})
    if lm:
        for art in schema.get("artefacts", []):
            if art.get("lifecycle") and not art.get("collection"):
                aid = art["id"]
                names.add(f"{aid}_header")
                if "history" in lm:
                    names.add(f"{aid}_history")
                if "approvals" in lm:
                    names.add(f"{aid}_approvals")
    return names


def _yaml_snippet_refs(schema: dict) -> dict[str, set[str]]:
    """Return {snippet_stem: {artefact_ids}} for every template: snippets/X.md in YAML."""
    refs: dict[str, set[str]] = {}
    for topic in schema.get("topics", []):
        for art_id, art_entry in topic.get("artefacts", {}).items():
            if not isinstance(art_entry, dict):
                continue
            tmpl = art_entry.get("template")
            entries = [tmpl] if isinstance(tmpl, str) else (tmpl or [])
            for t in entries:
                stem = Path(t).stem
                if stem:
                    refs.setdefault(stem, set()).add(art_id)
    return refs


def _template_regions_by_artefact(schema: dict) -> dict[str, list[str]]:
    """Map artefact_id → list of region names found in its *-template.md file."""
    result: dict[str, list[str]] = {}
    for art in schema.get("artefacts", []):
        aid = art["id"]
        # Educational template: {id}-template.md (hyphen), generator template: {id}_template.md (underscore)
        for tpl_name in (f"{aid}-template.md", f"{aid.replace('_', '-')}-template.md"):
            p = _TEMPLATES_DIR / tpl_name
            if p.exists():
                result[aid] = _regions_in_file(p)
                break
    return result


def _artefact_doc_expected_regions(
    schema: dict,
    artefact_id: str,
) -> dict[str, bool]:
    """Return {region_name: is_required} for regions expected in a rendered artefact document.

    Source of truth for region names: the artefact's *-template.md file (if it exists),
    because only regions that appear as <!-- #region X --> in the template will be present
    in the rendered output.  Falls back to snippet-backed YAML entries when no template exists.

    Required status is derived from YAML topic artefact entries (required: true).
    """
    # Determine region names from template file
    template_regions: set[str] = set()
    for tpl_name in (
        f"{artefact_id}-template.md",
        f"{artefact_id.replace('_', '-')}-template.md",
    ):
        p = _TEMPLATES_DIR / tpl_name
        if p.exists():
            template_regions = set(_regions_in_file(p))
            break

    if not template_regions:
        # No template file — fall back to YAML snippet references that have a file on disk
        for topic in schema.get("topics", []):
            art_entry = topic.get("artefacts", {}).get(artefact_id)
            if not isinstance(art_entry, dict):
                continue
            tmpl = art_entry.get("template")
            entries = [tmpl] if isinstance(tmpl, str) else (tmpl or [])
            for t in entries:
                stem = Path(t).stem
                if stem and (_SNIPPETS_DIR / f"{stem}.md").exists():
                    template_regions.add(stem)

    # Add lifecycle regions (they are always present in lifecycle artefacts)
    lm = schema.get("lifecycle_model", {})
    if lm:
        for art in schema.get("artefacts", []):
            if art.get("id") == artefact_id and art.get("lifecycle") and not art.get("collection"):
                template_regions.add(f"{artefact_id}_header")
                if "history" in lm:
                    template_regions.add(f"{artefact_id}_history")
                if "approvals" in lm:
                    template_regions.add(f"{artefact_id}_approvals")

    # Determine required status from YAML
    required_stems: set[str] = set()
    for topic in schema.get("topics", []):
        art_entry = topic.get("artefacts", {}).get(artefact_id)
        if not isinstance(art_entry, dict) or not art_entry.get("required"):
            continue
        tmpl = art_entry.get("template")
        entries = [tmpl] if isinstance(tmpl, str) else (tmpl or [])
        for t in entries:
            stem = Path(t).stem
            if stem:
                required_stems.add(stem)

    return {r: (r in required_stems) for r in template_regions}


# ── commands ──────────────────────────────────────────────────────────────────


@app.command()
def templates(
    schema: Path = typer.Option(_DEFAULT_SCHEMA, "--schema", help="Path to rpa-methodology.yaml"),
) -> None:
    """[Mode a] Check skill repo: YAML snippet refs ↔ snippet files ↔ template regions."""
    if not schema.exists():
        typer.echo(f"ERROR: schema not found: {schema}", err=True)
        raise typer.Exit(1)

    s = _load_schema(schema)
    r = _Report()

    # -- 1. YAML -> snippet files exist ----------------------------------------
    typer.echo("-- 1. YAML template references -> snippet files --")
    yaml_refs = _yaml_snippet_refs(s)
    for stem, art_ids in sorted(yaml_refs.items()):
        f = _SNIPPETS_DIR / f"{stem}.md"
        if f.exists():
            r.record(PASS, f"snippets/{stem}.md", f"exists (used by: {', '.join(sorted(art_ids))})")
        else:
            r.record(
                FAIL,
                f"snippets/{stem}.md",
                f"referenced by YAML ({', '.join(sorted(art_ids))}) but file not found",
            )
    typer.echo()

    # -- 2. Template regions -> known field or has snippet ---------------------
    typer.echo("-- 2. Template region markers -> YAML/snippet coverage --")
    known = _known_region_names(s)
    tpl_regions = _template_regions_by_artefact(s)
    for aid, regions in sorted(tpl_regions.items()):
        for region in regions:
            has_snippet = (_SNIPPETS_DIR / f"{region}.md").exists()
            is_known = region in known
            if has_snippet or is_known:
                r.record(
                    PASS,
                    f"{aid}: <!-- #region {region} -->",
                    "backed by snippet" if has_snippet else "backed by YAML field",
                )
            else:
                r.record(
                    WARN,
                    f"{aid}: <!-- #region {region} -->",
                    "SA-authored region -- no snippet and not a known field",
                )
    typer.echo()

    # -- 3. Orphan snippets (not referenced by any template) ------------------
    typer.echo("-- 3. Snippet files -> referenced by YAML or template --")
    # Collect all region names actually used in template files
    template_region_names: set[str] = set()
    for regions in tpl_regions.values():
        template_region_names.update(regions)
    for snippet in sorted(_SNIPPETS_DIR.glob("*.md")):
        stem = snippet.stem
        in_yaml = stem in yaml_refs
        in_templates = stem in template_region_names
        if in_yaml or in_templates:
            r.record(PASS, f"snippets/{stem}.md", "referenced")
        else:
            r.record(
                WARN,
                f"snippets/{stem}.md",
                "not referenced by any YAML template: entry or template <!-- #region -->",
            )
    typer.echo()

    # -- 4. arch-review sections -> snippets -----------------------------------
    typer.echo("-- 4. arch-review sections[] -> snippet files --")
    arch = next((a for a in s.get("artefacts", []) if a["id"] == "arch-review"), None)
    if arch:
        for sec in arch.get("sections", []):
            region = sec.get("region", "")
            source = sec.get("source", "?")
            if not region:
                continue
            f = _SNIPPETS_DIR / f"{region}.md"
            if f.exists():
                r.record(PASS, f"arch_review section: {region}", f"snippet exists (source: {source})")
            else:
                r.record(FAIL, f"arch_review section: {region}", f"snippet missing (source: {source})")
    else:
        r.record(WARN, "arch_review", "artefact not found in YAML")
    typer.echo()

    r.summary()
    raise typer.Exit(r.exit_code)


@app.command()
def docs(
    docs_dir: Path = typer.Argument(Path("docs"), help="Project docs directory"),
    schema: Path = typer.Option(_DEFAULT_SCHEMA, "--schema", help="Path to rpa-methodology.yaml"),
    artefact: str | None = typer.Option(None, "--artefact", "-a", help="Limit to one artefact id"),
) -> None:
    """[Mode b] Check project docs: find artefact files via file_glob and verify required regions."""
    if not schema.exists():
        typer.echo(f"ERROR: schema not found: {schema}", err=True)
        raise typer.Exit(1)
    if not docs_dir.is_dir():
        typer.echo(f"ERROR: docs directory not found: {docs_dir}", err=True)
        raise typer.Exit(1)

    s = _load_schema(schema)
    r = _Report()

    artefacts = [a for a in s.get("artefacts", []) if not a.get("generated")]
    if artefact:
        artefacts = [a for a in artefacts if a["id"] == artefact]
        if not artefacts:
            typer.echo(f"ERROR: artefact '{artefact}' not found in YAML", err=True)
            raise typer.Exit(1)

    for art in artefacts:
        aid = art["id"]
        glob = art.get("file_glob")
        if not glob:
            continue

        matches = sorted(docs_dir.glob(glob))
        if not matches:
            expected = _artefact_doc_expected_regions(s, aid)
            has_required = any(req for req in expected.values())
            if has_required:
                r.record(
                    WARN,
                    aid,
                    f"no file matching '{glob}' in {docs_dir} -- required regions cannot be checked",
                )
            continue

        for doc_path in matches:
            typer.echo(f"-- {aid}: {doc_path.name} --")
            present = set(_regions_in_file(doc_path))
            expected = _artefact_doc_expected_regions(s, aid)

            for region, required in sorted(expected.items()):
                if region in present:
                    r.record(PASS, f"{doc_path.name}: {region}", "present")
                elif required:
                    r.record(FAIL, f"{doc_path.name}: {region}", "required region missing")
                else:
                    r.record(WARN, f"{doc_path.name}: {region}", "optional region absent")

            # Regions present in doc but not in YAML
            for region in sorted(present - set(expected)):
                r.record(
                    WARN,
                    f"{doc_path.name}: {region}",
                    "region not recognised in YAML (SA-authored or stale)",
                )
            typer.echo()

    r.summary()
    raise typer.Exit(r.exit_code)


@app.command()
def fields(
    schema: Path = typer.Option(_DEFAULT_SCHEMA, "--schema", help="Path to rpa-methodology.yaml"),
) -> None:
    """[Mode c] Parse every owning template and check extracted field names against the schema.

    Covers scalars (flipped-table rows), list fields (N-col tables), and any other
    structure the parser produces.  A WARN means the parser would emit an 'unknown
    field' warning at project parse time — fix either the template label or the schema.
    """
    import sys

    _SKILL_PY = _SKILL_ROOT / "scripts"
    if str(_SKILL_PY) not in sys.path:
        sys.path.insert(0, str(_SKILL_PY))

    from cpm_rpa import schema as _schema_mod
    from cpm_rpa.parser import parse_document_full

    s = _load_schema(schema)
    schema_full = _schema_mod.load(schema)
    known: set[str] = set(_schema_mod.model_fields(schema_full).keys())

    # Owning artefacts in parse order (derived artefacts like arch-review are skipped)
    parse_order = ["pdd", "sdd", "tdd", "estimation", "roi", "project_plan"]
    r = _Report()

    for aid in parse_order:
        tpl: Path | None = None
        for name in (f"{aid}-template.md", f"{aid.replace('_', '-')}-template.md"):
            p = _TEMPLATES_DIR / name
            if p.exists():
                tpl = p
                break
        if tpl is None:
            continue

        typer.echo(f"-- {aid}: {tpl.name} --")
        extracted, origins = parse_document_full(tpl, schema_path=schema, artefact_id=aid)

        for key in sorted(extracted):
            if key in known:
                r.record(PASS, f"{aid}/{tpl.name}", f"field '{key}' known")
            else:
                if key in origins:
                    region, label = origins[key]
                    r.record(
                        WARN,
                        f"{aid}/{tpl.name}",
                        f"field '{key}' (from [{region}] row '{label}') not in schema",
                    )
                else:
                    r.record(WARN, f"{aid}/{tpl.name}", f"field '{key}' not in schema")
        typer.echo()

    r.summary()
    raise typer.Exit(r.exit_code)


if __name__ == "__main__":
    app()
