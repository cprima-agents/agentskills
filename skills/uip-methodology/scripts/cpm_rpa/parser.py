"""Parse rendered markdown documents back into structured project data.

The parser understands the template regions used by the renderer, plus a small
set of markdown conventions such as tables, bullet lists, and ADR inventory
entries.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from cpm_rpa import schema as _schema
from cpm_rpa.config import DEFAULT_SCHEMA
from cpm_rpa.ids import assign_ids_if_missing

_md = MarkdownIt().enable("table")
__all__ = [
    "extract_blocks",
    "parse_adr_inventory",
    "parse_document",
    "parse_document_full",
    "read_adr_file",
]

_ADR_HEADER_RE = re.compile(r"^####\s+(ADR-\d{4})\s*[—–\-]+\s*(.+)$", re.MULTILINE)
_ADR_INLINE_RE = re.compile(r"^\*\*(Status|Affects|Supersedes):\*\*\s+(.+)$", re.MULTILINE)
_ADR_BLOCK_RE = re.compile(
    r"\*\*(?P<key>Context|Decision|Rejected Options|Consequences):\*\*\s+(?P<val>.+?)(?=\n\*\*[A-Z]|\n---|\n####|\Z)",
    re.DOTALL,
)

# Matches <!-- #region name --> ... <!-- #endregion name --> with the same name (re.DOTALL)
BLOCK_RE = re.compile(
    r"<!--\s*#region\s+(\w+)\s*-->(.*?)<!--\s*#endregion\s+\1\s*-->",
    re.DOTALL,
)

# Markdown bullet list item: - text or * text
BULLET_RE = re.compile(r"^[-*+]\s+(.+)$")


def parse_adr_inventory(content: str) -> list[dict[str, Any]]:
    """Parse an `adr_inventory` region into a list of ADR dictionaries."""
    adrs = []
    matches = list(_ADR_HEADER_RE.finditer(content))
    for i, m in enumerate(matches):
        adr: dict[str, Any] = {"code": m.group(1).strip(), "title": m.group(2).strip()}
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]
        for fm in _ADR_INLINE_RE.finditer(body):
            key, val = fm.group(1).lower(), fm.group(2).strip()
            if key == "status":
                adr["status"] = val.lower()
            elif key == "affects":
                adr["affects"] = [s.strip() for s in val.split(",") if s.strip()]
            elif key == "supersedes":
                adr["supersedes"] = [s.strip() for s in val.split(",") if s.strip()]
        for bm in _ADR_BLOCK_RE.finditer(body):
            adr[bm.group("key").lower().replace(" ", "_")] = bm.group("val").strip()
        adrs.append(adr)
    return adrs


def extract_blocks(text: str) -> dict[str, str]:
    """Return the raw content for every named region in a document."""
    return {m.group(1): m.group(2).strip() for m in BLOCK_RE.finditer(text)}


def _to_field_name(label: str) -> str:
    """Convert a table row label into a schema-friendly field name."""
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def _cell_text(node: SyntaxTreeNode) -> str:
    """Extract plain text from a table cell node."""
    inline = next((c for c in node.children if c.type == "inline"), None)
    return inline.content.strip() if inline else ""


def _parse_table_node(table: SyntaxTreeNode) -> tuple[list[str], list[list[str]]]:
    """Return the header row and body rows from a parsed markdown table."""
    thead = next((c for c in table.children if c.type == "thead"), None)
    tbody = next((c for c in table.children if c.type == "tbody"), None)
    if not thead:
        return [], []
    header_row = next((c for c in thead.children if c.type == "tr"), None)
    headers = [_cell_text(th) for th in header_row.children if th.type == "th"] if header_row else []
    rows: list[list[str]] = []
    if tbody:
        for tr in tbody.children:
            if tr.type != "tr":
                continue
            cells = [_cell_text(td) for td in tr.children if td.type == "td"]
            while len(cells) < len(headers):
                cells.append("")
            rows.append(cells)
    return headers, rows


def _parse_region(
    text: str,
    derived: frozenset[str] = frozenset(),
) -> tuple[dict[str, Any] | list[dict[str, str]], dict[str, str], bool]:
    """Parse one region body into structured data.

    Returns:
    - parsed data
    - a label map for flipped tables
    - a flag indicating whether the region was a two-column Item/Value table

    Derived fields are skipped so the parser does not reintroduce stale values.
    """
    tree = SyntaxTreeNode(_md.parse(text))

    paragraphs = [c.children[0].content for c in tree.children if c.type == "paragraph" and c.children]
    table_nodes = [c for c in tree.children if c.type == "table"]

    if not table_nodes:
        return {}, {}, False

    headers, rows = _parse_table_node(table_nodes[0])
    if not headers:
        return {}, {}, False

    header_keys = [h.lower().replace(" ", "_") for h in headers]

    # ── 2-col flipped (| Item | Value |) ─────────────────────────────────────
    if len(headers) == 2 and header_keys == ["item", "value"]:
        result: dict[str, str] = {}
        label_map: dict[str, str] = {}
        for row in rows:
            key = _to_field_name(row[0])
            val = row[1].strip()
            if val and val != "[TBD]" and key not in derived:
                result[key] = val
                label_map[key] = row[0]
        return result, label_map, True

    # ── N-col table (containers, Item|Decision|Rationale, …) ─────────────────
    clean_rows: list[dict[str, str]] = []
    for row in rows:
        d = {header_keys[i]: row[i].strip() for i in range(len(header_keys))}
        d = {k: v for k, v in d.items() if v and v != "[TBD]" and k not in derived}
        if d:
            clean_rows.append(d)

    if not clean_rows:
        return {}, {}, False

    if paragraphs:
        return {"description": paragraphs[0], "decisions": clean_rows}, {}, False

    return clean_rows, {}, False


# Origin metadata helps the CLI explain where a parsed field came from when the
# schema no longer recognizes it.
FieldOrigin = tuple[str, str]


def parse_document_full(
    path: Path,
    schema_path: Path | None = None,
    artefact_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, FieldOrigin]]:
    """Extract structured data from a rendered document.

    Ownership filtering is optional but recommended: it prevents duplicate
    extraction when several artefacts reference the same topic.
    """
    sch = _schema.load(schema_path or DEFAULT_SCHEMA)
    derived = _schema.derived_field_names(sch)

    owned_regions: frozenset[str] | None = None
    if artefact_id is not None:
        ram = _schema.region_artefact_map(sch)
        owned_regions = frozenset(k for k, v in ram.items() if artefact_id in v)

    text = path.read_text(encoding="utf-8")
    result: dict[str, Any] = {}
    origins: dict[str, FieldOrigin] = {}

    for name, content in extract_blocks(text).items():
        if owned_regions is not None and name not in owned_regions:
            continue
        if not content or content == "[TBD]":
            continue
        if name == "adr_inventory":
            adrs = parse_adr_inventory(content)
            if adrs:
                assign_ids_if_missing(adrs, "dec_", "code")
                result["adrs"] = adrs
            continue
        parsed, label_map, is_flipped = _parse_region(content, derived)
        if is_flipped:
            result.update(parsed)
            for key, label in label_map.items():
                origins[key] = (name, label)
        elif parsed:
            if name not in derived:
                result[name] = parsed
        else:
            bullets = [
                m.group(1)
                for line in content.splitlines()
                if (m := BULLET_RE.match(line.strip()))
                and m.group(1) != "[TBD]"
                and not m.group(1).startswith("Step [TBD]")
            ]
            if bullets:
                result[name] = bullets

    # Auto-assign stable IDs to list items that lack them. Existing IDs are
    # preserved so manual overrides remain stable.
    assign_ids_if_missing(result.get("containers", []), "cmp", "name")
    assign_ids_if_missing(result.get("entities", []), "obj", "name")
    assign_ids_if_missing(result.get("effort_items", []), "est", "component_id", "catalog")
    assign_ids_if_missing(result.get("process_steps", []), "act", "step")

    # Merge per-kind observation regions into a single observations list. The
    # region name supplies the kind when the table does not.
    _KIND_REGIONS = [
        ("observations_discovery", "observation"),
        ("observations_improvement", "improvement"),
        ("observations_removal", "removal"),
        ("observations_issues", "issue"),
    ]
    obs_merged: list[dict] = list(result.pop("observations", None) or [])
    for region_key, kind in _KIND_REGIONS:
        items = result.pop(region_key, None)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item.setdefault("kind", kind)
            obs_merged.extend(items)
    for item in result.pop("notes", None) or []:
        if isinstance(item, dict):
            obs_merged.append(item)
    if obs_merged:
        result["observations"] = obs_merged
        assign_ids_if_missing(obs_merged, "obs", "title")

    return result, origins


def parse_document(
    path: Path,
    schema_path: Path | None = None,
    artefact_id: str | None = None,
) -> dict[str, Any]:
    """Convenience wrapper that returns only the parsed data dictionary."""
    data, _ = parse_document_full(path, schema_path, artefact_id)
    return data


# Regexes for standalone ADR files (H1 title + **Inline:** fields + ## H2 sections).
# These differ from the inventory-embedded format (_ADR_HEADER_RE / _ADR_BLOCK_RE above).
_SA_TITLE_RE = re.compile(r"^#\s+(ADR-\d{4})\s*[—–\-]+\s*(.+)$", re.MULTILINE)
_SA_INLINE_RE = re.compile(r"^\*\*(Status|Affects|Supersedes):\*\*\s+(.+?)\s*$", re.MULTILINE)
_SA_SECTION_RE = re.compile(r"^##\s+([^\n]+)\n(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)

_KNOWN_SECTIONS = {"context", "decision", "rejected_options", "consequences"}


def read_adr_file(path: Path) -> dict[str, Any]:
    """Parse a standalone ADR markdown file into template-ready data."""
    text = path.read_text(encoding="utf-8")
    adr: dict[str, Any] = {}

    m = _SA_TITLE_RE.search(text)
    if m:
        adr["code"] = m.group(1).strip()
        adr["title"] = m.group(2).strip()

    for fm in _SA_INLINE_RE.finditer(text):
        key, val = fm.group(1).lower(), fm.group(2).strip()
        if key == "status":
            adr["status"] = val.lower()
        elif key == "affects":
            adr["affects"] = [s.strip() for s in val.split(",") if s.strip()]
        elif key == "supersedes":
            adr["supersedes"] = [s.strip() for s in val.split(",") if s.strip()]

    for sm in _SA_SECTION_RE.finditer(text):
        key = sm.group(1).strip().lower().replace(" ", "_")
        if key in _KNOWN_SECTIONS:
            adr[key] = sm.group(2).strip()

    assign_ids_if_missing([adr], "dec_", "code")
    return adr
