# ADR-0005 — Document-oriented architecture knowledge graph

**Status:** Accepted

## Context

The skill produces several related artefacts — PDD, SDD, arch-review, ROI, project plan, TDD — from a
shared YAML data model. Each artefact renders a subset of model fields using Jinja2 templates, and
humans amend the generated documents between render cycles. The problem: objects that appear in
multiple artefacts (containers, decisions, observations, effort items) had no stable identity across
documents. A container listed in the SDD had no programmatic link to the same container cited in the
arch-review estimation table. Re-parsing after human edits would create duplicate nodes or silently
lose traces.

A secondary problem: the semantic relationships the documents encode — "this ADR affects the SDD and
arch-review", "this observation relates to this container", "this effort item is estimated for this
component" — were invisible at the data layer. The YAML was a flat property bag, not a graph.

## Decision

The system is designed as a **document-oriented knowledge graph** in which:

1. **Nodes are typed, named objects** — containers, ADRs, observations, effort items, data entities —
   each carrying a stable `id` and optionally a human-readable `code`.
2. **Artefacts are projections** — each artefact file is a view over the graph rendered by Jinja2
   templates, not a standalone document.
3. **Renderers are forward projections** — they transform graph data into markdown documents.
4. **Parsers are inverse projections** — they recover graph data from human-amended markdown back into
   structured data.
5. **Round-trip invariants** ensure no object's `id` changes across a render → edit → parse cycle.

### Stable graph nodes

Every node class carries a stable `id` field assigned by `assign_ids_if_missing()`:

| Node class | Prefix | Key field(s) used for hash |
|---|---|---|
| Component / Container | `cmp_` | `name` |
| Decision (ADR) | `dec_` | `code` |
| Observation | `obs_` | `title` |
| Effort item | `est_` | `component_id`, `catalog` |
| Data entity | `ent_` | `name` |
| Process step | `act_` | `step` |

The ID is `prefix + sha256(key_fields)[:6]`. Six characters provide collision resistance at typical
project scale (≤ 100 nodes per class). IDs are immutable once assigned — `assign_ids_if_missing()`
skips any node that already carries an `id`.

### Dual identity for human-coded objects

Some node classes carry both a stable `id` and a human-readable `code` that appears in headings and
cross-references:

| Field | Example | Role |
|---|---|---|
| `id` | `dec_8f31aa` | Stable trace node — never changes, used by tools |
| `code` | `ADR-0001` | Human display code — parsed from heading, shown in tables |

Currently only ADRs use dual identity. The pattern is available for extension to Risks (`R-001`),
Issues (`I-014`), and Test Cases (`TC-022`) when those node types require cross-artefact traceability.

### Semantic ownership

`rpa-methodology.yaml` declares per topic which artefact **owns** each region (writes the
authoritative version) and which artefacts **parse from** it (read and republish). This makes
provenance explicit at the schema level:

```yaml
topic: Container architecture
artefacts:
  sdd:
    owns: true
    template: [snippets/containers.md, ...]
  arch_review:
    parse_from: sdd
```

`region_artefact_map()` in `schema.py` exposes this ownership graph to the CLI so that
`parse <file> --artefact sdd` extracts only regions the SDD owns, avoiding double-ingestion when
multiple artefacts reference the same data.

### Traceability edges

Edges are encoded as YAML fields within node entries:

| Edge type | Field | Example |
|---|---|---|
| ADR affects artefact | `affects: [sdd, tdd]` | `dec_8f31aa` affects SDD and TDD |
| ADR supersedes ADR | `supersedes: [ADR-0001]` | Replaces an older decision |
| Observation links component | `component_id: cmp_a1b2c3` | Finding attributed to a component |
| Effort item targets component | `component_id: cmp_a1b2c3` | Estimate for a named component |

### Renderers

Renderers (`renderer.py`) are forward projections: they read `project-data.yaml`, resolve the Jinja2
template for the requested artefact, preprocess `<!-- #region name -->` markers to include the
corresponding snippet, and write the rendered markdown. Renderers never assign IDs — they only
emit whatever `id` values are already in the data.

### Parsers

Parsers (`parser.py`) are inverse projections: they extract named blocks from rendered documents
using the `<!-- #region name --> ... <!-- #endregion name -->` boundary convention, then decode each
block into structured data matching the schema. After extraction, `assign_ids_if_missing()` is called
to assign stable IDs to any new nodes the human added since the last render. Parsers are artefact-aware:
the `--artefact` flag restricts extraction to regions owned by the specified artefact, preventing
double-ingestion of shared data.

### Round-trip invariants

A render → edit → parse cycle must satisfy:

1. Every node `id` present before render is present after parse.
2. No new `id` value is created for an object that was already assigned one.
3. Human additions (new rows in a rendered table) acquire an `id` on next parse via
   `assign_ids_if_missing()`.
4. Human deletions (removed rows) leave the `id` orphaned — not an error; the object is simply
   no longer represented in that artefact view.

These invariants are enforced by:
- Calling `assign_ids_if_missing()` at every parse ingest point.
- Never generating IDs at render time.
- Emitting `id` values in rendered output (via snippet templates) so the parser can recover them.

### Derived artefacts

Some artefacts contain no primary-authored content — they aggregate and republish data owned by other
artefacts. The arch-review is a canonical example: it reads containers from the SDD, ADRs from the
SDD, estimation from the estimation artefact, ROI from the ROI artefact. Derived artefacts are
parse-safe: their `region_artefact_map()` entries list the owning artefact, so the parser routes
extracted data back to the correct owner rather than treating the arch-review as a second source of
truth for SDD-owned data.

## Rejected Options

**Sequential integers as the only identity (ADR-0001, R-001):** Readable but unstable — reordering
rows in a table reassigns IDs, and merge conflicts cannot be resolved without re-numbering. Retained
as `code` (display layer) for ADRs, not as `id` (identity layer).

**UUIDs:** Correct, but verbose in YAML and rendered tables. The 6-character sha256 prefix is compact,
deterministic from content, and collision-resistant at project scale.

**No stable identity (plain-text matching):** Objects matched by title string across artefacts break
on any rename. Not viable for traceability.

**Graph database:** Overkill for a document set that fits in a single YAML file. The YAML-as-graph
approach is self-contained, version-control-friendly, and survives installation into any user project
directory.

## Consequences

- `assign_ids_if_missing()` must be called at every ingest point; omitting it allows unidentified
  nodes to enter the graph.
- Snippet templates must emit `id` values in rendered tables; snippets that omit the `id` column
  prevent round-trip recovery of existing IDs.
- New node types require: a registered prefix in `assign_ids_if_missing()`, `model:` entries in
  `rpa-methodology.yaml`, and snippets that include an `id` column in rendered output.
- The `code` field is distinct from `id` and may be reassigned without breaking graph integrity;
  `id` is immutable once assigned.
- The dual-identity pattern is currently applied only to ADRs; extending it to Risks, Issues, and
  Test Cases is a future decision when those types require cross-artefact traceability.
- Adding a new edge type requires: a schema field in the relevant `model:` block, rendering logic
  in the snippet, and parser support in `parser.py` (or it flows automatically for free-form YAML
  fields that the parser preserves verbatim).
