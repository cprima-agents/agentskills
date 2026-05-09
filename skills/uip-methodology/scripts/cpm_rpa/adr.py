"""Extract individual ADR files from a rendered document.

The `adr_inventory` region is used as a compact authoring format, then expanded
into one markdown file per ADR for easier review and maintenance.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import typer  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402

from cpm_rpa.config import TEMPLATES_DIR  # noqa: E402
from cpm_rpa.parser import extract_blocks, parse_adr_inventory  # noqa: E402

app = typer.Typer(help="Parse adr_inventory region from a rendered document back to individual ADR markdown files.")
__all__ = ["app", "parse"]

_TITLE_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _render_adr_md(adr: dict[str, Any]) -> str:
    """Render one ADR dictionary through the ADR template."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), keep_trailing_newline=True)
    return env.get_template("adr-template.md").render(**adr)


@app.command()
def parse(
    file: Path = typer.Argument(help="Rendered document containing an <!-- #region adr_inventory --> block"),
    output_dir: Path = typer.Option(
        Path("docs/adr"), "--output-dir", "-o", help="Directory to write ADR markdown files"
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing ADR files"),
) -> None:
    """Write one markdown ADR file per inventory entry."""
    if not file.exists():
        typer.echo(f"ERROR: {file} not found.", err=True)
        raise typer.Exit(1)

    inventory = extract_blocks(file.read_text(encoding="utf-8")).get("adr_inventory", "")
    if not inventory:
        typer.echo("WARN: no adr_inventory region found in document.", err=True)
        raise typer.Exit(0)

    adrs = parse_adr_inventory(inventory)
    if not adrs:
        typer.echo("WARN: adr_inventory region contains no parseable ADR entries.", err=True)
        raise typer.Exit(0)

    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for adr in adrs:
        adr_id = adr.get("code", "ADR-XXXX")
        title_slug = _TITLE_SLUG_RE.sub("-", adr.get("title", "").lower()).strip("-")
        out_path = output_dir / f"{adr_id.lower()}-{title_slug}.md"
        if out_path.exists() and not overwrite:
            typer.echo(f"SKIP: {out_path} (use --overwrite to replace)")
            continue
        out_path.write_text(_render_adr_md(adr), encoding="utf-8")
        typer.echo(f"Written: {out_path}")
        written += 1

    typer.echo(f"Done: {written} ADR file(s) written to {output_dir}")


if __name__ == "__main__":
    app()
