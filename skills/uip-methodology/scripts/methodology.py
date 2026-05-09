"""Inspect the methodology schema that drives the RPA skill.

This module is the read-only browser for the schema. It exposes commands for
topics, models, artefact coverage, elicitation prompts, and enumerations.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from io import StringIO  # noqa: E402

import typer  # noqa: E402
from cpm_rpa import schema as _schema  # noqa: E402
from cpm_rpa.config import DEFAULT_SCHEMA  # noqa: E402
from ruamel.yaml import YAML as _YAML  # noqa: E402

app = typer.Typer(
    help="Inspect rpa-methodology.yaml — list topics, models, artefact coverage, and interview questions.",
    no_args_is_help=True,
)
__all__ = [
    "app",
    "artefacts",
    "coverage",
    "enum_list",
    "glue",
    "interview",
    "model",
    "models",
    "topic",
    "topics",
]

_SCHEMA_OPT = typer.Option(DEFAULT_SCHEMA, "--schema", help="Path to rpa-methodology.yaml")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load(schema_path: Path) -> dict[str, Any]:
    return _schema.load(schema_path)


def _row(*widths: int):
    """Return a fixed-width row formatter for the given column widths."""

    def fmt(*cells) -> str:
        return "  ".join(str(c).ljust(w) for c, w in zip(cells, widths, strict=False))

    return fmt


def _find_topic(data: dict, name: str) -> dict[str, Any]:
    needle = name.lower()
    matches = [t for t in data.get("topics", []) if needle in t["topic"].lower()]
    if not matches:
        typer.echo(f"No topic matching '{name}'.", err=True)
        raise typer.Exit(1)
    if len(matches) > 1:
        typer.echo(f"Ambiguous — {len(matches)} topics match '{name}':", err=True)
        for m in matches:
            typer.echo(f"  {m['topic']}", err=True)
        raise typer.Exit(1)
    return matches[0]


# ---------------------------------------------------------------------------
# topics
# ---------------------------------------------------------------------------


@app.command()
def topics(
    schema: Path = _SCHEMA_OPT,
    kind: str | None = typer.Option(None, "--kind", "-k", help="Filter by semantics.kind"),
    artefact: str | None = typer.Option(None, "--artefact", "-a", help="Filter to topics present in artefact"),
) -> None:
    """List all topics — optionally filtered by kind or artefact."""
    data = _load(schema)
    row = _row(4, 38, 12, 40)
    typer.echo(row("#", "Topic", "Kind", "Artefacts"))
    typer.echo(row("-" * 3, "-" * 37, "-" * 11, "-" * 39))
    n = 0
    for t in data.get("topics", []):
        k = t.get("semantics", {}).get("kind", "")
        if kind and k != kind:
            continue
        arts = t.get("artefacts", {})
        if artefact and artefact not in arts:
            continue
        n += 1
        typer.echo(row(str(n), t["topic"], k, ", ".join(arts.keys())))
    typer.echo(f"\n{n} topic(s)")


# ---------------------------------------------------------------------------
# topic
# ---------------------------------------------------------------------------


@app.command()
def topic(
    name: str = typer.Argument(help="Topic name — partial, case-insensitive match"),
    schema: Path = _SCHEMA_OPT,
) -> None:
    """Show the full YAML definition of one topic."""
    data = _load(schema)
    t = _find_topic(data, name)
    _buf = StringIO()
    _y = _YAML()
    _y.default_flow_style = False
    _y.dump(t, _buf)
    typer.echo(_buf.getvalue())


# ---------------------------------------------------------------------------
# models
# ---------------------------------------------------------------------------


@app.command()
def models(
    schema: Path = _SCHEMA_OPT,
    artefact: str | None = typer.Option(None, "--artefact", "-a", help="Filter to topics present in artefact"),
) -> None:
    """List all topics that define a concept.model."""
    data = _load(schema)
    row = _row(38, 7, 52)
    typer.echo(row("Topic", "Fields", "Field names"))
    typer.echo(row("-" * 37, "-" * 6, "-" * 51))
    n = 0
    for t in data.get("topics", []):
        m = t.get("concept", {}).get("model", {})
        if not m:
            continue
        if artefact and artefact not in t.get("artefacts", {}):
            continue
        n += 1
        typer.echo(row(t["topic"], str(len(m)), ", ".join(m.keys())))
    typer.echo(f"\n{n} topic(s) with a model")


# ---------------------------------------------------------------------------
# model
# ---------------------------------------------------------------------------


@app.command()
def model(
    name: str = typer.Argument(help="Topic name — partial, case-insensitive match"),
    schema: Path = _SCHEMA_OPT,
) -> None:
    """Show the concept.model field table for one topic."""
    data = _load(schema)
    needle = name.lower()
    matches = [t for t in data.get("topics", []) if needle in t["topic"].lower() and t.get("concept", {}).get("model")]
    if not matches:
        typer.echo(f"No topic with a model matching '{name}'.", err=True)
        raise typer.Exit(1)
    if len(matches) > 1:
        typer.echo(f"Ambiguous — {len(matches)} topics match '{name}':", err=True)
        for m in matches:
            typer.echo(f"  {m['topic']}", err=True)
        raise typer.Exit(1)
    t = matches[0]
    typer.echo(f"Model: {t['topic']}\n")
    row = _row(30, 10, 9, 28, 30)
    typer.echo(row("Field", "Type", "Required", "Enum / item type", "Derived / notes"))
    typer.echo(row("-" * 29, "-" * 9, "-" * 8, "-" * 27, "-" * 29))

    def _print_field(fname: str, fdef: Any, indent: str = "") -> None:
        if not isinstance(fdef, dict):
            typer.echo(row(indent + fname, str(fdef), "", "", ""))
            return
        typ = fdef.get("type", "")
        req = "yes" if fdef.get("required") else ""
        derived = str(fdef.get("derived", "") or fdef.get("description", "") or "")
        enum_val = fdef.get("enum", "")
        if isinstance(enum_val, list):
            enum_col = ", ".join(str(e) for e in enum_val)
        elif enum_val:
            enum_col = str(enum_val)
        else:
            enum_col = ""
        item = fdef.get("item", {})
        is_struct_item = (
            isinstance(item, dict) and item and not item.get("type")  # struct items have no top-level 'type' key
        )
        if isinstance(item, dict) and item and not is_struct_item:
            sub_type = item.get("type", "")
            sub_enum = item.get("enum", "")
            if isinstance(sub_enum, list):
                sub_enum = ", ".join(str(e) for e in sub_enum)
            enum_col = f"item: {sub_type}" + (f" enum={sub_enum}" if sub_enum else "")
        typer.echo(row(indent + fname, typ, req, enum_col, derived))
        if is_struct_item:
            for sub_name, sub_def in item.items():
                _print_field(sub_name, sub_def, indent + "  ")

    for fname, fdef in t["concept"]["model"].items():
        _print_field(fname, fdef)


# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------


@app.command()
def coverage(
    artefact_id: str | None = typer.Argument(None, help="Artefact id — omit to list valid ids"),
    schema: Path = _SCHEMA_OPT,
) -> None:
    """List all topics present in an artefact, with section, ownership, and template."""
    data = _load(schema)
    art_index = {a["id"]: a for a in data.get("artefacts", [])}
    if artefact_id is None:
        typer.echo("Valid artefacts: " + ", ".join(art_index.keys()))
        return
    if artefact_id not in art_index:
        typer.echo(
            f"Unknown artefact '{artefact_id}'.\nValid: {', '.join(art_index.keys())}",
            err=True,
        )
        raise typer.Exit(1)
    typer.echo(f"Coverage: {art_index[artefact_id]['label']}\n")
    row = _row(8, 38, 5, 8, 36)
    typer.echo(row("Section", "Topic", "Owns", "Required", "Template"))
    typer.echo(row("-" * 7, "-" * 37, "-" * 4, "-" * 7, "-" * 35))
    n = 0
    for t in data.get("topics", []):
        entry = t.get("artefacts", {}).get(artefact_id)
        if entry is None:
            continue
        n += 1
        if isinstance(entry, dict):
            section = str(entry.get("section", ""))
            owns = "yes" if entry.get("owns") else ""
            required = "yes" if entry.get("required") else ""
            tmpl = str(entry.get("template", ""))
        else:
            section = owns = required = tmpl = ""
        typer.echo(row(section, t["topic"], owns, required, tmpl))
    typer.echo(f"\n{n} topic(s) in {artefact_id}")


# ---------------------------------------------------------------------------
# interview
# ---------------------------------------------------------------------------


@app.command()
def interview(
    schema: Path = _SCHEMA_OPT,
    artefact: str | None = typer.Option(None, "--artefact", "-a", help="Restrict to topics in artefact"),
) -> None:
    """Dump all elicitation questions as a numbered list."""
    data = _load(schema)
    n = 0
    for t in data.get("topics", []):
        if artefact and artefact not in t.get("artefacts", {}):
            continue
        q = t.get("acquisition", {}).get("interview", {}).get("question")
        if not q:
            continue
        n += 1
        typer.echo(f"{n}. [{t['topic']}]")
        for line in q.splitlines():
            typer.echo(f"   {line}")
        typer.echo()
    if n == 0:
        typer.echo("No interview questions found.")
    else:
        typer.echo(f"{n} question(s)")


# ---------------------------------------------------------------------------
# artefacts
# ---------------------------------------------------------------------------


@app.command()
def artefacts(
    schema: Path = _SCHEMA_OPT,
) -> None:
    """List all defined artefacts with their file glob and flags."""
    data = _load(schema)
    row = _row(14, 22, 35, 10, 10, 10)
    typer.echo(row("ID", "Label", "File glob", "Client", "Lifecycle", "Collection"))
    typer.echo(row("-" * 13, "-" * 21, "-" * 34, "-" * 9, "-" * 9, "-" * 9))
    for a in data.get("artefacts", []):
        typer.echo(
            row(
                a["id"],
                a.get("label", ""),
                a.get("file_glob", ""),
                "yes" if a.get("client_facing") else "",
                "yes" if a.get("lifecycle") else "",
                "yes" if a.get("collection") else "",
            )
        )


# ---------------------------------------------------------------------------
# glue
# ---------------------------------------------------------------------------


def _glue_detail(t: dict[str, Any]) -> None:
    typer.echo(f"Topic:  {t['topic']}")
    typer.echo(f"Kind:   {t.get('semantics', {}).get('kind', '')}")

    typer.echo()
    acq = t.get("acquisition", {})
    modes = acq.get("modes", [])
    typer.echo(f"Acquisition:  {', '.join(modes) if modes else '—'}")
    for mode in modes:
        detail = acq.get(mode)
        if not isinstance(detail, dict):
            continue
        for key, val in detail.items():
            if val:
                typer.echo(f"  {mode}.{key}:")
                for line in str(val).splitlines():
                    typer.echo(f"    {line}")

    typer.echo()
    tr = t.get("transforms", {})
    typer.echo("Transforms:")
    typer.echo(f"  to_markdown:   {tr.get('to_markdown', '—')}")
    typer.echo(f"  from_markdown: {tr.get('from_markdown', '—')}")


@app.command()
def glue(
    name: str | None = typer.Argument(
        None,
        help="Topic name (partial match). Omit to list all topics.",
    ),
    schema: Path = _SCHEMA_OPT,
    kind: str | None = typer.Option(None, "--kind", "-k", help="Filter by semantics.kind (all-topics mode only)."),
) -> None:
    """Show semantics, acquisition, and transforms — the glue that connects topics to documents.

    With no argument: compact table for all topics.
    With a topic name: full detail for one topic.
    """
    data = _load(schema)

    if name:
        t = _find_topic(data, name)
        _glue_detail(t)
        return

    row = _row(4, 38, 12, 16, 18, 18)
    typer.echo(row("#", "Topic", "Kind", "Modes", "to_markdown", "from_markdown"))
    typer.echo(row("-" * 3, "-" * 37, "-" * 11, "-" * 15, "-" * 17, "-" * 17))
    for i, t in enumerate(data.get("topics", []), 1):
        if kind and t.get("semantics", {}).get("kind", "") != kind:
            continue
        k = t.get("semantics", {}).get("kind", "")
        modes = ", ".join(t.get("acquisition", {}).get("modes", []))
        tr = t.get("transforms", {})
        to_md = Path(tr["to_markdown"]).name if tr.get("to_markdown") else ""
        from_md = Path(tr["from_markdown"]).name if tr.get("from_markdown") else ""
        typer.echo(row(str(i), t["topic"], k, modes, to_md, from_md))


# ---------------------------------------------------------------------------
# enums
# ---------------------------------------------------------------------------


@app.command("enums")
def enum_list(
    name: str | None = typer.Argument(None, help="Enum name — partial, case-insensitive match"),
    schema: Path = _SCHEMA_OPT,
) -> None:
    """List all named enums defined in the schema, with their id/label pairs.

    With no argument: show all enum names and their option count.
    With a name: show the full id/label table for that enum.
    """
    data = _load(schema)
    enums: dict = data.get("enums", {})
    if not enums:
        typer.echo("No enums defined in schema.")
        raise typer.Exit(0)

    if name:
        needle = name.lower()
        matches = [k for k in enums if needle in k.lower()]
        if not matches:
            typer.echo(f"No enum matching '{name}'.", err=True)
            raise typer.Exit(1)
        for enum_name in matches:
            typer.echo(f"Enum: {enum_name}\n")
            row = _row(24, 40)
            typer.echo(row("  ID", "Label"))
            typer.echo(row("  " + "-" * 22, "-" * 39))
            for entry in enums[enum_name]:
                typer.echo(row("  " + entry.get("id", ""), entry.get("label", "")))
            typer.echo()
        return

    row = _row(28, 7, 50)
    typer.echo(row("Enum", "Options", "Values (id)"))
    typer.echo(row("-" * 27, "-" * 6, "-" * 49))
    for enum_name, entries in enums.items():
        ids = ", ".join(e.get("id", "") for e in entries)
        typer.echo(row(enum_name, str(len(entries)), ids))
    typer.echo(f"\n{len(enums)} enum(s)")


@app.command()
def regions(
    schema: Path = _SCHEMA_OPT,
) -> None:
    """List every <!-- #region X --> found in all artefact templates, with its artefact."""
    import re

    _REGION_RE = re.compile(r"<!--\s*#region\s+(\w+)\s*-->")
    _SKILL_ROOT = Path(__file__).resolve().parent.parent
    _TEMPLATES_DIR = _SKILL_ROOT / "assets" / "templates"

    data = _load(schema)
    row = _row(18, 42, 10)
    typer.echo(row("Artefact", "Region", "Has snippet"))
    typer.echo(row("-" * 17, "-" * 41, "-" * 9))

    total = 0
    for art in data.get("artefacts", []):
        aid = art["id"]
        for tpl_name in (f"{aid}-template.md", f"{aid.replace('_', '-')}-template.md"):
            p = _TEMPLATES_DIR / tpl_name
            if not p.exists():
                continue
            names = _REGION_RE.findall(p.read_text(encoding="utf-8"))
            for name in names:
                has_snippet = (_TEMPLATES_DIR / "snippets" / f"{name}.md").exists()
                typer.echo(row(aid, name, "yes" if has_snippet else ""))
                total += 1
            break

    typer.echo(f"\n{total} region(s) across all templates")


if __name__ == "__main__":
    app()
