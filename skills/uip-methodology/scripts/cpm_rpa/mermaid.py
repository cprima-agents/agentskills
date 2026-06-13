"""Mermaid diagram renderer for code-structure YAML files.

Passes:
  1. parse    — caller loads YAML and passes nodes list
  2. index    — build NodeGraph (by_id, children, depth, ancestors)
  3. validate — return warnings list (orphan parents, unreachable nodes)
  4. render   — NodeGraph -> Mermaid markdown fenced block
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# ── shapes / styles ───────────────────────────────────────────────────────────

SHAPES: dict[str, tuple[str, str]] = {
    "process": ("([", "])"),
    "phase":   ("[",  "]"),
    "module":  ("[",  "]"),
    "unit":    ("[[", "]]"),
}

# Solarized palette reference:
#   base03=#002b36  base02=#073642  base01=#586e75  base00=#657b83
#   base0=#839496   base1=#93a1a1   base2=#eee8d5   base3=#fdf6e3
#   green=#859900   orange=#cb4b16  red=#dc322f     cyan=#2aa198
#   blue=#268bd2    violet=#6c71c4  yellow=#b58900  magenta=#d33682

COLORSCHEMES: dict[str, dict[str, str]] = {
    "solarized-light": {
        "":            "fill:#fdf6e3,color:#657b83,stroke:#93a1a1",
        "implemented": "fill:#eee8d5,color:#586e75,stroke:#859900,stroke-width:2px",
        "stub":        "fill:#93a1a1,color:#002b36,stroke:#b58900,stroke-width:2px",
        "pending":     "fill:#93a1a1,color:#002b36,stroke:#b58900",
        "in-progress": "fill:#268bd2,color:#fdf6e3,stroke:#073642,stroke-width:2px",
    },
    "default": {
        "":            "fill:#f8f9fa,color:#495057,stroke:#ced4da",
        "implemented": "fill:#2d6a4f,color:#fff,stroke:#1b4332",
        "stub":        "fill:#e76f51,color:#fff,stroke:#c45c3a",
        "pending":     "fill:#adb5bd,color:#000,stroke:#6c757d",
        "in-progress": "fill:#f4a261,color:#000,stroke:#e76f51",
    },
}

STATUS_LABEL: dict[str, str] = {
    "implemented": "[ok]",
    "stub":        "[stub]",
    "pending":     "[?]",
    "in-progress": "[wip]",
}

# C4 level each node type maps to — embedded in diagram title/comment
C4_LEVEL: dict[str, str] = {
    "process": "C4-L2-Container",
    "phase":   "C4-L3-Component-Group",
    "module":  "C4-L3-Component",
    "unit":    "C4-L4-Code",
}


# ── pass 2: index ─────────────────────────────────────────────────────────────

@dataclass
class NodeGraph:
    nodes:     list[dict]
    by_id:     dict[str, dict]       = field(default_factory=dict)
    children:  dict[str, list[str]]  = field(default_factory=dict)
    depth:     dict[str, int]        = field(default_factory=dict)
    ancestors: dict[str, list[str]]  = field(default_factory=dict)


def build_graph(nodes: list[dict]) -> NodeGraph:
    g = NodeGraph(nodes=nodes)

    for n in nodes:
        g.by_id[n["id"]] = n
        g.children.setdefault(n["id"], [])

    for n in nodes:
        p = n.get("parent")
        if p and p != "~":
            g.children.setdefault(str(p), [])
            g.children[str(p)].append(n["id"])

    roots = [n["id"] for n in nodes if not n.get("parent") or n.get("parent") == "~"]
    for r in roots:
        g.depth[r] = 1
        g.ancestors[r] = []

    queue = list(roots)
    while queue:
        cur = queue.pop(0)
        for child_id in g.children.get(cur, []):
            g.depth[child_id] = g.depth[cur] + 1
            g.ancestors[child_id] = g.ancestors[cur] + [cur]
            queue.append(child_id)

    return g


# ── pass 3: validate ──────────────────────────────────────────────────────────

def validate(g: NodeGraph) -> list[str]:
    """Return warning strings; caller decides where to emit them."""
    warnings: list[str] = []
    for n in g.nodes:
        p = n.get("parent")
        if p and p != "~" and p not in g.by_id:
            warnings.append(f"{n['id']} references unknown parent '{p}'")
        if n["id"] not in g.depth:
            warnings.append(f"{n['id']} unreachable (cycle or orphan)")
    return warnings


# ── pass 4: render helpers ────────────────────────────────────────────────────

def _sid(node_id: str) -> str:
    return node_id.replace("-", "_")


def _short_label(node: dict) -> str:
    name  = node.get("name") or node["id"]
    badge = STATUS_LABEL.get(node.get("status", ""), "")
    f     = node.get("file")
    fname = Path(f).name if f and f != "~" else ""
    return f"{name} {badge}<br/>{fname}" if fname else f"{name} {badge}"


def _node_decl(node: dict) -> str:
    nid = _sid(node["id"])
    open_, close = SHAPES.get(node.get("type", "module"), ("[", "]"))
    return f'{nid}{open_}"{_short_label(node)}"{close}'


def _is_visible(
    node: dict,
    g: NodeGraph,
    max_depth: int | None,
    allowed_types: set[str] | None,
) -> bool:
    if max_depth is not None and g.depth.get(node["id"], 999) > max_depth:
        return False
    if allowed_types is not None and node.get("type") not in allowed_types:
        return False
    return True


# ── render: flow ──────────────────────────────────────────────────────────────

def _render_children(
    parent_id: str,
    g: NodeGraph,
    max_depth: int | None,
    allowed_types: set[str] | None,
    declared: set[str],
    indent: str = "    ",
) -> list[str]:
    """Recursively declare visible descendants + their edges inside a subgraph."""
    decls: list[str] = []
    edges: list[str] = []

    for child_id in g.children.get(parent_id, []):
        child = g.by_id[child_id]
        if not _is_visible(child, g, max_depth, allowed_types):
            continue
        decls.append(f"{indent}{_node_decl(child)}")
        declared.add(child_id)
        sub = _render_children(child_id, g, max_depth, allowed_types, declared, indent)
        decls.extend(sub)
        if parent_id in declared:
            edges.append(f"{indent}{_sid(parent_id)} --> {_sid(child_id)}")

    return decls + edges


def render_flow(
    g: NodeGraph,
    max_depth: int | None,
    allowed_types: set[str] | None,
    status_fill: dict[str, str],
    c4_title: str = "",
) -> list[str]:
    declared: set[str] = set()
    header = f"%% {c4_title}" if c4_title else "%% C4-L3-Component diagram"
    lines = ["```mermaid", "flowchart TD", f"  {header}"]

    process_nodes = [n for n in g.nodes if n.get("type") == "process"]
    phase_nodes   = [n for n in g.nodes if n.get("type") == "phase"]

    for p in process_nodes:
        if max_depth is None or g.depth.get(p["id"], 1) <= max_depth:
            lines.append(f"  {_node_decl(p)}")
            declared.add(p["id"])

    for ph in phase_nodes:
        ph_id = ph["id"]
        if max_depth is not None and g.depth.get(ph_id, 999) > max_depth:
            continue
        child_lines = _render_children(ph_id, g, max_depth, allowed_types, declared)
        lines.append(f"  subgraph {_sid(ph_id)}[\"{ph.get('name', ph_id)}\"]")
        lines.extend(child_lines)
        lines.append("  end")
        declared.add(ph_id)

    lines.append("")

    visible_phases = [ph for ph in phase_nodes if ph["id"] in declared]
    if process_nodes and visible_phases:
        chain = [_sid(process_nodes[0]["id"])] + [_sid(ph["id"]) for ph in visible_phases]
        lines.append("  " + " --> ".join(chain))

    lines.append("")
    for node in g.nodes:
        if node["id"] not in declared:
            continue
        style = status_fill.get(node.get("status", "")) or status_fill.get("")
        if style:
            lines.append(f"  style {_sid(node['id'])} {style}")

    lines.append("```")
    return lines


# ── render: tree ──────────────────────────────────────────────────────────────

def render_tree(
    g: NodeGraph,
    max_depth: int | None,
    allowed_types: set[str] | None,
    status_fill: dict[str, str],
    c4_title: str = "",
) -> list[str]:
    declared: set[str] = set()
    header = f"%% {c4_title}" if c4_title else "%% C4-L3-Component diagram"
    lines = ["```mermaid", "flowchart TD", f"  {header}"]

    for node in g.nodes:
        if not _is_visible(node, g, max_depth, allowed_types):
            continue
        nid    = node["id"]
        parent = node.get("parent")
        declared.add(nid)

        if not parent or parent == "~":
            lines.append(f"  {_node_decl(node)}")
        else:
            pnode = g.by_id.get(str(parent))
            if pnode and _is_visible(pnode, g, max_depth, allowed_types):
                lines.append(f"  {_sid(str(parent))} --> {_node_decl(node)}")
            else:
                lines.append(f"  {_node_decl(node)}")

    lines.append("")
    for node in g.nodes:
        if node["id"] not in declared:
            continue
        style = status_fill.get(node.get("status", "")) or status_fill.get("")
        if style:
            lines.append(f"  style {_sid(node['id'])} {style}")

    lines.append("```")
    return lines


# ── c4 title helper ───────────────────────────────────────────────────────────

def c4_title_for(
    nodes: list[dict],
    g: NodeGraph,
    stem: str,
    max_depth: int | None,
    allowed_types: set[str] | None,
    scheme_name: str,
) -> tuple[str, str]:
    """Return (c4_title, depth_tag)."""
    type_order = ["unit", "module", "phase", "process"]
    visible_types = {
        n.get("type") for n in nodes
        if (max_depth is None or g.depth.get(n["id"], 999) <= max_depth)
        and (allowed_types is None or n.get("type") in allowed_types)
    }
    deepest   = next((t for t in type_order if t in visible_types), "module")
    c4_level  = C4_LEVEL.get(deepest, "C4-L3-Component")
    depth_tag = f"-d{max_depth}" if max_depth else ""
    title     = f"{c4_level} | {stem}{depth_tag} | colorscheme:{scheme_name}"
    return title, depth_tag
