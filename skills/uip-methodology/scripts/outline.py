"""Inspect template structure without expanding snippet bodies.

The outline command is a documentation aid. It shows headings, comments, and
region markers so maintainers can review template structure quickly.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import typer  # noqa: E402
from cpm_rpa.config import TEMPLATES_DIR  # noqa: E402

# Windows terminals default to cp1252; templates contain Unicode (arrows, dashes).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_REGION_OPEN = re.compile(r"<!--\s*#region\s+(\S+)\s*-->")
_REGION_CLOSE = re.compile(r"<!--\s*#endregion\s+\S+\s*-->")
_HEADING_RE = re.compile(r"^(#{1,6})\s")

app = typer.Typer(
    help="Show template content with example-data regions collapsed.",
    no_args_is_help=False,
    invoke_without_command=True,
)
__all__ = ["app", "main"]


@app.command()
def main(
    files: list[Path] = typer.Argument(
        None,
        help="Files to scan. Defaults to all *.md in assets/templates/ (not snippets/).",
    ),
    depth: int = typer.Option(
        6,
        "--depth",
        "-d",
        min=1,
        max=6,
        help="Collapse sections deeper than this level to heading-only (default: show all).",
    ),
    numbers: bool = typer.Option(False, "--numbers", "-n", help="Show line numbers."),
) -> None:
    """Show template structure — headings, prose, and HTML comments — with
    #region blocks replaced by a single marker line.

    Sections deeper than --depth are shown as headings only; their content is
    suppressed. Useful for reviewing section purpose and spotting formatting
    errors without wading through example data.

    Defaults to all *.md in assets/templates/ (not snippets/).
    """
    targets: list[Path] = list(files) if files else sorted(TEMPLATES_DIR.glob("*.md"))

    if not targets:
        typer.echo("No files found.", err=True)
        raise typer.Exit(1)

    for path in targets:
        if not path.exists():
            typer.echo(f"WARN: {path} not found — skipped.", err=True)
            continue

        label = path.name
        typer.echo(f"\n{label}")
        typer.echo("=" * len(label))

        in_region: str | None = None
        collapsed: bool = False

        for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.rstrip()
            prefix = f"{lineno:4d}  " if numbers else ""

            # Inside a region — skip until close tag
            if in_region is not None:
                if _REGION_CLOSE.search(line):
                    in_region = None
                continue

            # Region open — emit a single marker, enter skip mode
            m = _REGION_OPEN.search(line)
            if m:
                in_region = m.group(1)
                typer.echo(f"{prefix}<!-- [region: {in_region}] -->")
                continue

            # Heading — always emit; update collapsed state
            hm = _HEADING_RE.match(line)
            if hm:
                lvl = len(hm.group(1))
                collapsed = lvl > depth
                typer.echo(f"{prefix}{line}")
                continue

            # All other content — emit only when not collapsed
            if not collapsed:
                typer.echo(f"{prefix}{line}")


if __name__ == "__main__":
    app()
