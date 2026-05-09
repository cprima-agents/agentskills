"""Render Jinja2 templates from structured project data.

The renderer is schema-aware: it derives missing values, folds in project.json
metadata when available, and expands template regions backed by snippet files.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Undefined

from cpm_rpa import schema as _schema
from cpm_rpa.config import DEFAULT_SCHEMA, TEMPLATES_DIR
from cpm_rpa.ids import gen_id as _gen_id
from cpm_rpa.parser import read_adr_file

_SAFE_GLOBALS: dict[str, Any] = {"__builtins__": {}, "round": round, "abs": abs}
__all__ = ["render"]


def _to_slug(name: str) -> str:
    """Convert a PascalCase or camelCase identifier into snake_case."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _to_pascal(name: str) -> str:
    """Convert a snake_case identifier into PascalCase."""
    return "".join(w.capitalize() for w in name.split("_"))


def _to_cs_type(field: dict[str, Any]) -> str:
    """Derive a C# type string from a schema field definition.

    Nullability is handled separately by the template layer.
    """
    if field.get("csharp_type"):
        return field["csharp_type"]
    if field.get("item_type"):
        return f"List<{field['item_type']}Dto>"
    return {"integer": "int", "number": "double", "boolean": "bool", "bool": "bool"}.get(
        field.get("type", "string"), "string"
    )


def _to_stage(file_path: str) -> str:
    """Derive a pipeline stage name from a workflow path."""
    p = Path(file_path)
    if p.parent.name.lower() == "process":
        return p.stem.lower()
    return "—"


# Template regions let the repo keep one source of truth for reusable content.
# When a region has a matching snippet file, we replace the inline body with an
# include so the same region can be rendered and parsed back later.
_REGION_RE = re.compile(
    r"<!--\s*#region\s+(\w+)\s*-->(.*?)<!--\s*#endregion\s+\1\s*-->",
    re.DOTALL,
)


def _expand_regions(text: str) -> str:
    """Replace region bodies with snippet includes when a snippet exists.

    Regions without a backing snippet stay inline. That keeps SA-authored prose
    and diagrams intact on re-render.
    """
    snippets_dir = TEMPLATES_DIR / "snippets"

    def _sub(m: re.Match[str]) -> str:
        name = m.group(1)
        if (snippets_dir / f"{name}.md").exists():
            return f"<!-- #region {name} -->\n{{% include 'snippets/{name}.md' %}}\n<!-- #endregion {name} -->"
        return m.group(0)

    return _REGION_RE.sub(_sub, text)


def _resolve_derived(data: dict[str, Any], schema_path: Path) -> dict[str, Any]:
    """Evaluate derived fields and inject computed values into the render context.

    User-supplied values win. Derived values are only filled when they are
    missing, and chained formulas are resolved by re-running until stable.
    """
    fields = _schema.model_fields(_schema.load(schema_path))
    derived = {name: defn["derived"] for name, defn in fields.items() if "derived" in defn}
    if not derived:
        return data

    result = dict(data)
    for _ in range(len(derived) + 1):
        changed = False
        for field, formula in derived.items():
            if field in result:
                continue  # user-provided or already computed — never overwrite
            ns = {k: v for k, v in result.items() if isinstance(v, (int, float))}
            try:
                value = eval(formula, _SAFE_GLOBALS, ns)  # noqa: S307
                result[field] = round(float(value), 2)
                changed = True
            except Exception:  # noqa: BLE001
                pass  # inputs not yet available — retry next pass or skip
        if not changed:
            break
    return result


def _build_config_sections(
    configs: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    """Build the template context used for configuration tables."""
    envs = list(configs.keys())
    section_names: list[str] = []
    for env_data in configs.values():
        for s in env_data:
            if not s.startswith("_") and s not in section_names:
                section_names.append(s)

    sections = []
    for sec_name in section_names:
        prop_names: list[str] = []
        for env_data in configs.values():
            for p in env_data.get(sec_name, {}):
                if not p.startswith("_") and p not in prop_names:
                    prop_names.append(p)

        properties: list[dict[str, Any]] = []
        for prop_name in prop_names:
            py_type = "string"
            for env_data in configs.values():
                val = env_data.get(sec_name, {}).get(prop_name)
                if val is not None:
                    if isinstance(val, bool):
                        py_type = "bool"
                    elif isinstance(val, int):
                        py_type = "int"
                    elif isinstance(val, float):
                        py_type = "double"
                    elif isinstance(val, dict):
                        py_type = "asset"
                    break
            prop: dict[str, Any] = {"name": prop_name, "type": py_type}
            for env, env_data in configs.items():
                val = env_data.get(sec_name, {}).get(prop_name)
                if val is None:
                    prop[env] = "—"
                elif isinstance(val, bool):
                    prop[env] = str(val).lower()
                elif isinstance(val, dict):
                    folder = val.get("folder", "")
                    asset = val.get("assetName", "")
                    prop[env] = f"{folder}/{asset}" if folder else asset
                else:
                    prop[env] = str(val)
            properties.append(prop)
        sections.append({"name": sec_name, "properties": properties})
    return envs, sections


def render(
    artefact: str,
    data: dict[str, Any],
    output_path: Path,
    schema_path: Path | None = None,
    project_json_path: Path | None = None,
    config_paths: dict[str, Path] | None = None,
    adr_dir: Path | None = None,
) -> None:
    data = _resolve_derived(data, schema_path or DEFAULT_SCHEMA)
    if adr_dir and adr_dir.is_dir() and "adrs" not in data:
        adrs = [read_adr_file(p) for p in sorted(adr_dir.glob("*.md"))]
        if adrs:
            data["adrs"] = adrs
    if config_paths:
        loaded = {}
        for env, p in config_paths.items():
            if p.exists():
                with p.open("rb") as f:
                    loaded[env] = tomllib.load(f)
        if loaded:
            envs, sections = _build_config_sections(loaded)
            if "config_envs" not in data:
                data["config_envs"] = envs
            if "config_sections" not in data:
                data["config_sections"] = sections
    if project_json_path and project_json_path.exists():
        proj = json.loads(project_json_path.read_text(encoding="utf-8"))
        data["project"] = proj
        for src, dst in [
            ("studioVersion", "studio_version"),
            ("expressionLanguage", "expression_language"),
            ("targetFramework", "target_framework"),
        ]:
            if dst not in data and proj.get(src):
                data[dst] = proj[src]
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        undefined=Undefined,  # missing variables silently render as ""
        keep_trailing_newline=True,
    )
    env.filters["to_slug"] = _to_slug
    env.filters["to_stage"] = _to_stage
    env.filters["to_pascal"] = _to_pascal
    env.filters["to_cs_type"] = _to_cs_type
    env.filters["by_kind"] = lambda lst, kind: [
        x for x in (lst if lst else []) if isinstance(x, dict) and x.get("kind") == kind
    ]
    env.globals["gen_id"] = _gen_id
    template_file = f"{artefact}-template.md"
    raw = (TEMPLATES_DIR / template_file).read_text(encoding="utf-8")
    tmpl = env.from_string(_expand_regions(raw))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tmpl.render(**data), encoding="utf-8")
