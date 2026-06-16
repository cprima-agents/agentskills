"""Deterministic markdown linter for UiPath RPA project artefacts.

Checks region integrity, heading structure, placeholder discipline, markdown
hygiene, table consistency, and diagram fences. Intended to be run by the
uipath-rpa-design skill immediately after writing or amending any artefact.

Usage:
    uv run skills/uipath-rpa-design/scripts/lint_docs.py docs/
    uv run skills/uipath-rpa-design/scripts/lint_docs.py docs/ppo-objection-pdd.md
    uv run skills/uipath-rpa-design/scripts/lint_docs.py docs/ --strict
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from cpm_rpa import schema as _schema  # noqa: E402
from cpm_rpa.config import DEFAULT_DOCS, DEFAULT_SCHEMA  # noqa: E402

# ---------------------------------------------------------------------------
# Check level defaults
# ---------------------------------------------------------------------------

FAIL = "FAIL"
WARN = "WARN"

_CHECK_LEVEL: dict[str, str] = {
    "R01": FAIL,
    "R02": FAIL,
    "R03": FAIL,
    "H01": FAIL,
    "H02": WARN,
    "H03": FAIL,
    "P01": WARN,
    "P02": WARN,
    "P03": WARN,
    "P04": WARN,
    "M01": WARN,
    "M02": WARN,
    "M03": WARN,
    "M04": WARN,
    "T01": WARN,
    "D01": FAIL,
}

# ---------------------------------------------------------------------------
# Issue + Report
# ---------------------------------------------------------------------------


@dataclass(order=True)
class Issue:
    path: Path
    lineno: int | None
    level: str
    code: str
    message: str

    def format(self) -> str:
        loc = f"{self.path}:{self.lineno}" if self.lineno else str(self.path)
        return f"[{self.level}] {self.code} {loc}: {self.message}"


class _Report:
    def __init__(self, strict: bool = False) -> None:
        self.strict = strict
        self._issues: list[Issue] = []

    def _level(self, code: str) -> str:
        base = _CHECK_LEVEL.get(code, WARN)
        return FAIL if (self.strict and base == WARN) else base

    def add(self, issue: Issue) -> None:
        self._issues.append(issue)

    def emit(self, path: Path, lineno: int | None, code: str, msg: str) -> None:
        self.add(Issue(path, lineno, self._level(code), code, msg))

    def summary(self, file_count: int) -> None:
        for issue in sorted(self._issues, key=lambda i: (i.path, i.lineno or 0, i.code)):
            typer.echo(issue.format())
        fails = sum(1 for i in self._issues if i.level == FAIL)
        warns = sum(1 for i in self._issues if i.level == WARN)
        label = "FAILED" if (fails or (self.strict and warns)) else "OK"
        typer.echo(f"\n{file_count} file(s) — {fails} failed, {warns} warning(s) [{label}]")

    @property
    def exit_code(self) -> int:
        fails = sum(1 for i in self._issues if i.level == FAIL)
        warns = sum(1 for i in self._issues if i.level == WARN)
        return 1 if (fails or (self.strict and warns)) else 0


# ---------------------------------------------------------------------------
# File context + line iterator
# ---------------------------------------------------------------------------


@dataclass
class _FileContext:
    path: Path
    raw_lines: list[str]
    in_fence: bool = False
    fence_marker: str = ""
    fence_lang: str = ""
    fence_open_lineno: int = 0
    in_front_matter: bool = False
    front_matter_closed: bool = False
    unclosed_mermaid_lineno: int | None = None


_FENCE_RE = re.compile(r"^(`{3,}|~{3,})(.*)")


def _iter_lines(ctx: _FileContext):
    """Yield (lineno, raw_line, is_code, is_front_matter) updating ctx state."""
    expecting_fm_open = True

    for lineno, raw in enumerate(ctx.raw_lines, 1):
        line = raw.rstrip("\r\n")

        # Front-matter: first line only
        if expecting_fm_open:
            expecting_fm_open = False
            if line.strip() == "---":
                ctx.in_front_matter = True
                yield lineno, line, False, True
                continue

        if ctx.in_front_matter:
            if line.strip() == "---":
                ctx.in_front_matter = False
                ctx.front_matter_closed = True
                yield lineno, line, False, True
                continue
            yield lineno, line, False, True
            continue

        # Fence detection
        m = _FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            lang = m.group(2).strip().lower()
            if not ctx.in_fence:
                ctx.in_fence = True
                ctx.fence_marker = marker
                ctx.fence_lang = lang
                ctx.fence_open_lineno = lineno
                yield lineno, line, True, False
                continue
            elif len(marker) >= len(ctx.fence_marker) and marker[0] == ctx.fence_marker[0]:
                ctx.in_fence = False
                ctx.fence_lang = ""
                ctx.fence_marker = ""
                yield lineno, line, True, False
                continue

        yield lineno, line, ctx.in_fence, False

    if ctx.in_fence and ctx.fence_lang == "mermaid":
        ctx.unclosed_mermaid_lineno = ctx.fence_open_lineno


# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

_REGION_OPEN_RE = re.compile(r"<!--\s*#region\s+(\S+)\s*-->")
_REGION_CLOSE_RE = re.compile(r"<!--\s*#endregion\s+(\S+)\s*-->")
_VALID_NAME_RE = re.compile(r"^\w+$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
_HR_RE = re.compile(r"^-{3,}\s*$")
_TABLE_ROW_RE = re.compile(r"^\|.*\|")
_SEP_ROW_RE = re.compile(r"^\|[\s|:\-]+\|$")
_DOUBLE_SPACE_RE = re.compile(r"\S {2,}\S")
_TOKEN_RE = re.compile(r"<([a-z][a-z0-9-]*)>", re.IGNORECASE)

_HTML_TAGS = frozenset(
    {
        "a",
        "b",
        "br",
        "code",
        "div",
        "details",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "s",
        "span",
        "strong",
        "summary",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
)

# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------


def check_regions(path: Path, lines: list[str], report: _Report) -> None:
    """R01 R02 R03 — scan all lines including inside fences."""
    open_stack: list[tuple[str, int]] = []

    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip("\r\n")
        m_open = _REGION_OPEN_RE.search(line)
        m_close = _REGION_CLOSE_RE.search(line)

        if m_open:
            name = m_open.group(1)
            if not _VALID_NAME_RE.match(name):
                report.emit(path, lineno, "R03", f"invalid region name '{name}' — must match \\w+")
            open_stack.append((name, lineno))

        if m_close:
            name = m_close.group(1)
            if not _VALID_NAME_RE.match(name):
                report.emit(path, lineno, "R03", f"invalid region name '{name}' in #endregion")
            idx = next(
                (i for i in reversed(range(len(open_stack))) if open_stack[i][0] == name),
                None,
            )
            if idx is None:
                report.emit(path, lineno, "R02", f"#endregion '{name}' has no prior #region")
            else:
                open_stack.pop(idx)

    for name, lineno in open_stack:
        report.emit(path, lineno, "R01", f"orphaned <!-- #region {name} --> (no matching #endregion)")


def check_headings(path: Path, annotated: list[tuple], report: _Report) -> None:
    """H01 H02 H03."""
    headings: list[tuple[int, int]] = []
    for lineno, line, is_code, _is_fm in annotated:
        if is_code:
            continue
        m = _HEADING_RE.match(line)
        if m:
            headings.append((lineno, len(m.group(1))))

    if not headings:
        report.emit(path, None, "H01", "no headings found in document")
        return

    # H03: first heading must be H1
    first_ln, first_lvl = headings[0]
    if first_lvl != 1:
        report.emit(path, first_ln, "H03", f"first heading is H{first_lvl}, expected H1")

    # H01: exactly one H1
    h1s = [(ln, lvl) for ln, lvl in headings if lvl == 1]
    if len(h1s) == 0:
        report.emit(path, None, "H01", "no H1 found")
    elif len(h1s) > 1:
        for ln, _ in h1s[1:]:
            report.emit(path, ln, "H01", "duplicate H1 — document must have exactly one H1")

    # H02: no level gaps between consecutive headings
    for (prev_ln, prev_lvl), (cur_ln, cur_lvl) in zip(headings, headings[1:], strict=False):
        if cur_lvl > prev_lvl + 1:
            report.emit(
                path,
                cur_ln,
                "H02",
                f"heading gap — H{prev_lvl} at line {prev_ln} followed by H{cur_lvl} (skips H{prev_lvl + 1})",
            )


def check_placeholders(path: Path, annotated: list[tuple], report: _Report) -> None:
    """P01 P02 P03 P04."""
    tbd = sme = default = 0
    for lineno, line, is_code, _is_fm in annotated:
        if is_code:
            continue
        tbd += len(re.findall(r"\[TBD\]", line, re.IGNORECASE))
        sme += len(re.findall(r"\[SME REVIEW\]", line, re.IGNORECASE))
        default += len(re.findall(r"\[DEFAULT\]", line, re.IGNORECASE))
        for m in _TOKEN_RE.finditer(line):
            tag = m.group(1).lower()
            if tag not in _HTML_TAGS:
                report.emit(path, lineno, "P04", f"unreplaced template token '<{m.group(1)}>'")

    if tbd:
        report.emit(path, None, "P01", f"{tbd} [TBD] item(s) remaining")
    if sme:
        report.emit(path, None, "P02", f"{sme} [SME REVIEW] item(s) remaining")
    if default:
        report.emit(path, None, "P03", f"{default} [DEFAULT] item(s) remaining")


def check_hygiene(path: Path, annotated: list[tuple], ctx: _FileContext, report: _Report) -> None:
    """M01 M02 M03 M04."""
    blank_run = 0
    blank_warned = False

    for lineno, line, is_code, is_fm in annotated:
        stripped = line.strip()

        # M03: consecutive blank lines
        if stripped == "":
            blank_run += 1
            if blank_run > 2 and not blank_warned:
                report.emit(path, lineno, "M03", "more than 2 consecutive blank lines")
                blank_warned = True
            continue
        else:
            blank_run = 0
            blank_warned = False

        if is_fm or is_code:
            continue

        # M01: standalone --- outside front matter
        if _HR_RE.match(line):
            report.emit(path, lineno, "M01", "standalone --- (horizontal rule) outside front matter")

        # M02: hard tab
        if "\t" in line:
            report.emit(path, lineno, "M02", "hard tab character outside code block")

        # M04: double space mid-line (not trailing line-break)
        if not line.endswith("  ") and _DOUBLE_SPACE_RE.search(line):
            report.emit(path, lineno, "M04", "double space mid-line")


def check_tables(path: Path, annotated: list[tuple], report: _Report) -> None:
    """T01: inconsistent column count across table rows."""

    def _col_count(row: str) -> int:
        inner = row.strip().strip("|")
        return len(inner.split("|"))

    header_cols: int | None = None
    in_table = False

    for lineno, line, is_code, is_fm in annotated:
        if is_code or is_fm:
            in_table = False
            header_cols = None
            continue

        if _TABLE_ROW_RE.match(line):
            if _SEP_ROW_RE.match(line):
                in_table = True
                continue
            if not in_table:
                header_cols = _col_count(line)
            else:
                cols = _col_count(line)
                if header_cols is not None and cols != header_cols:
                    report.emit(
                        path,
                        lineno,
                        "T01",
                        f"table row has {cols} column(s), header has {header_cols}",
                    )
        else:
            if in_table:
                in_table = False
                header_cols = None


# ---------------------------------------------------------------------------
# File-level orchestrator
# ---------------------------------------------------------------------------


def lint_file(path: Path, artefact_id: str | None, report: _Report, *, snippet: bool = False) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.emit(path, None, "R01", f"cannot read file: {exc}")
        return

    lines = text.splitlines()
    ctx = _FileContext(path=path, raw_lines=lines)
    annotated = list(_iter_lines(ctx))

    check_regions(path, lines, report)
    if not snippet:
        check_headings(path, annotated, report)
    check_placeholders(path, annotated, report)
    check_hygiene(path, annotated, ctx, report)
    check_tables(path, annotated, report)

    if ctx.unclosed_mermaid_lineno is not None:
        report.emit(path, ctx.unclosed_mermaid_lineno, "D01", "```mermaid fence opened but not closed")


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def _collect_files(
    targets: list[Path],
    artefact_override: str | None,
    snippet: bool,
    sch: dict[str, Any],
) -> list[tuple[Path, str | None]]:
    paths: list[Path] = []
    for target in targets:
        if target.is_file():
            paths.append(target)
        else:
            paths.extend(sorted(target.rglob("*.md")))

    result = []
    for p in paths:
        aid = artefact_override or _schema.detect_artefact(sch, p)
        result.append((p, aid, snippet))
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

app = typer.Typer(help=__doc__, no_args_is_help=True)


@app.command()
def main(
    targets: list[Path] = typer.Argument(None, help="Files or directories to lint (default: docs/)"),
    schema: Path = typer.Option(DEFAULT_SCHEMA, "--schema", help="Path to rpa-methodology.yaml"),
    artefact: str | None = typer.Option(None, "--artefact", "-a", help="Override artefact detection"),
    snippet: bool = typer.Option(False, "--snippet", help="Treat targets as partial fragments (skip H01/H03)"),
    strict: bool = typer.Option(False, "--strict", help="Treat WARNs as FAILs for exit code"),
) -> None:
    if not schema.exists():
        typer.echo(f"ERROR: schema not found: {schema}", err=True)
        raise typer.Exit(1)

    resolved: list[Path] = targets or [DEFAULT_DOCS]
    for t in resolved:
        if not t.exists():
            typer.echo(f"ERROR: target not found: {t}", err=True)
            raise typer.Exit(1)

    sch = _schema.load(schema)
    report = _Report(strict=strict)
    pairs = _collect_files(resolved, artefact, snippet, sch)

    for path, aid, is_snippet in pairs:
        lint_file(path, aid, report, snippet=is_snippet)

    report.summary(len(pairs))
    raise typer.Exit(report.exit_code)


if __name__ == "__main__":
    app()
