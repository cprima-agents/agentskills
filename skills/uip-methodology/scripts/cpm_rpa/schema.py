"""Load and query the methodology schema used by the RPA skill.

The schema drives topic coverage, field extraction, artefact ownership, and
round-trip parsing/rendering behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML as _YAML

from cpm_rpa.config import DEFAULT_SCHEMA

_safe = _YAML(typ="safe")
__all__ = [
    "artefact_glob",
    "derived_field_names",
    "detect_artefact",
    "enum_labels",
    "find_artefact_file",
    "load",
    "model_fields",
    "region_artefact_map",
    "resolve_label",
]


def load(schema_path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    """Load the methodology YAML into a Python dictionary."""
    return _safe.load(schema_path.read_text(encoding="utf-8"))


def model_fields(schema: dict) -> dict[str, dict]:
    """Return a flat field map for top-level and lifecycle schema fields."""
    fields: dict[str, dict] = {}
    for topic in schema.get("topics", []):
        for name, defn in topic.get("concept", {}).get("model", {}).items():
            fields[name] = {**defn, "topic": topic["topic"]}
    for group in schema.get("shared", []):
        for name, defn in group.get("model", {}).items():
            fields[name] = {**defn, "topic": group["name"]}
    lm = schema.get("lifecycle_model", {})
    if lm:
        header_fields = lm.get("header", {})
        for artefact in schema.get("artefacts", []):
            if artefact.get("lifecycle"):
                prefix = artefact["id"]
                label = artefact["label"]
                for fname, fdefn in header_fields.items():
                    fields[f"{prefix}_{fname}"] = {**fdefn, "topic": f"{label} lifecycle"}
                if "history" in lm:
                    fields[f"{prefix}_history"] = {**lm["history"], "topic": f"{label} lifecycle"}
                if "approvals" in lm:
                    fields[f"{prefix}_approvals"] = {
                        **lm["approvals"],
                        "topic": f"{label} lifecycle",
                    }
    return fields


def derived_field_names(schema: dict) -> frozenset[str]:
    """Return every field name that is computed from a schema expression."""
    names: set[str] = set()
    for topic in schema.get("topics", []):
        for name, defn in topic.get("concept", {}).get("model", {}).items():
            if not isinstance(defn, dict):
                continue
            if "derived" in defn:
                names.add(name)
            item = defn.get("item", {})
            if isinstance(item, dict):
                for sub_name, sub_defn in item.items():
                    if isinstance(sub_defn, dict) and "derived" in sub_defn:
                        names.add(sub_name)
    for group in schema.get("shared", []):
        for name, defn in group.get("model", {}).items():
            if isinstance(defn, dict) and "derived" in defn:
                names.add(name)
    return frozenset(names)


def detect_artefact(schema: dict, path: Path) -> str | None:
    """Return the artefact id whose file glob matches the given path."""
    for a in schema.get("artefacts", []):
        glob = a.get("file_glob")
        if glob and path.match(glob):
            return a["id"]
    return None


def region_artefact_map(schema: dict) -> dict[str, frozenset[str]]:
    """Map each region name to the artefacts that own it.

    Region names are derived from:
    - concept.model top-level field names
    - snippet stems listed in artefacts.<parse_from>.template entries
    - lifecycle regions ({artefact_id}_header/history/approvals) for lifecycle artefacts

    A region may be owned by multiple artefacts (e.g. 'volume' appears in both
    the PDD and the SDD capacity section).
    """
    acc: dict[str, set[str]] = {}
    for topic in schema.get("topics", []):
        parse_from = topic.get("transforms", {}).get("parse_from")
        # Concept model fields belong to the parse_from artefact.
        if parse_from:
            for fname in topic.get("concept", {}).get("model", {}).keys():
                acc.setdefault(fname, set()).add(parse_from)
        # Owned template regions belong to the artefact that owns them, regardless
        # of parse_from — e.g. observations_issues is owned by tdd even though the
        # topic's parse_from is pdd.
        for aid, art_entry in topic.get("artefacts", {}).items():
            if not isinstance(art_entry, dict) or not art_entry.get("owns"):
                continue
            tmpl_val = art_entry.get("template")
            templates = [tmpl_val] if isinstance(tmpl_val, str) else (tmpl_val or [])
            for tmpl in templates:
                region = Path(tmpl).stem
                if region:
                    acc.setdefault(region, set()).add(aid)
    # Lifecycle regions: {artefact_id}_header/history/approvals for non-collection artefacts
    lm = schema.get("lifecycle_model", {})
    if lm:
        for artefact in schema.get("artefacts", []):
            if artefact.get("lifecycle") and not artefact.get("collection"):
                aid = artefact["id"]
                acc.setdefault(f"{aid}_header", set()).add(aid)
                if "history" in lm:
                    acc.setdefault(f"{aid}_history", set()).add(aid)
                if "approvals" in lm:
                    acc.setdefault(f"{aid}_approvals", set()).add(aid)
    return {k: frozenset(v) for k, v in acc.items()}


def resolve_label(schema: dict, enum_name: str, id_value: str) -> str:
    """Resolve an enum id to its human-readable label."""
    for entry in schema.get("enums", {}).get(enum_name, []):
        if entry.get("id") == id_value:
            return entry["label"]
    return "[TBD]"


def enum_labels(schema: dict, enum_name: str) -> dict[str, str]:
    """Return the id-to-label mapping for a named enum."""
    return {e["id"]: e["label"] for e in schema.get("enums", {}).get(enum_name, [])}


def artefact_glob(schema: dict, artefact_id: str) -> str | None:
    """Return the file glob configured for an artefact."""
    for a in schema.get("artefacts", []):
        if a["id"] == artefact_id:
            return a.get("file_glob")
    return None


def find_artefact_file(docs_dir: Path, artefact_id: str, schema: dict) -> Path | None:
    """Find the first document in *docs_dir* that matches an artefact glob."""
    glob = artefact_glob(schema, artefact_id)
    if not glob:
        return None
    matches = sorted(docs_dir.glob(glob))
    return matches[0] if matches else None
