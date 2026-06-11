# ADR-0004 — Generator architecture: interview, project data, renderer, parser, Jinja2 templates

**Status:** Accepted

## Context

The skill must produce RPA project documents (PDD, SDD, etc.) from information gathered during a structured interview. The naive approach — an LLM filling in a markdown template directly — has two problems:

1. **Assessment poisoning**: sample/illustrative content in a template looks like real content to a coverage checker.
2. **No round-trip**: once a human amends a generated document, there is no way to extract the changes back into structured data.

A secondary constraint: the skill is installed into the user's own repository. It has no control over the user's project structure, Python environment, or how data was collected. "Interview" is only one possible input source.

## Decision

### Input / Model / View / Output separation

```
Input sources
├── LLM interview      → populates project-data.yaml
├── Human-edited YAML  → directly amends project-data.yaml
└── Parse (see below)  → extracts from amended documents back into project-data.yaml

Model
└── ./docs/project-data.yaml   (user's project; one flat YAML keyed by model field names)

View
├── assets/templates/*.md           (main templates; human-readable, contain <!-- example --> blocks)
└── assets/templates/snippets/*.md  (Jinja2 snippets; rendering logic for structured sections)

Output
└── ./docs/<artefact>.md       (generated documents; default opinionated filenames)
```

The LLM interview is one input path, not the only one. `project-data.yaml` is the canonical model instance; anything that produces or modifies it is a valid input source.

### Three-tier template placeholder convention

Templates contain three kinds of content:

| Marker | Meaning | Filled by |
|---|---|---|
| `{{ variable }}` | Scalar substitution | Generator |
| `{% for item in list %}` | Repeating rows | Generator |
| `[TBD]` / `[SME REVIEW]` | Human-fill gap | Human |
| `<!-- #region name -->...<!-- #endregion name -->` | Snippet indirection point (templates) / round-trip marker (output) | Renderer (preprocessed) / Parser |

The `<!-- #region name -->` / `<!-- #endregion name -->` pair (VS Code region convention) serves two roles depending on context:
- **In template source**: the block body is a static illustrative example. The renderer replaces the entire block with `<!-- #region name -->{% include "snippets/name.md" %}<!-- #endregion name -->` before Jinja2 processes the file.
- **In rendered output**: the same markers delimit the content the parser extracts for round-trip data recovery. The Jinja2 rendering logic lives in `assets/templates/snippets/name.md`, not in the main template.

### Named output markers for round-trip parsing

Every Jinja2 block that produces structured content emits VS Code region markers in the rendered output:

```
<!-- #region field_name -->
| ... table rows ... |
<!-- #endregion field_name -->
```

The marker name is identical to the model field name and the Jinja2 variable name. This creates a stable, human-visible boundary that survives editing in any markdown editor. The parser extracts blocks by name using a single regex with a backreference, then derives field names from column headers directly via `h.lower().replace(" ", "_")` — no mapping dictionary is needed.

### Jinja2 templates as generators

Templates are `.md` files containing Jinja2 syntax. They are not scaffolds — they are views in an MVC sense. The schema (`rpa-methodology.yaml` `model:` keys) is the contract; the template is the rendering logic; `project-data.yaml` is the data instance.

Missing variables render silently as empty string (`jinja2.Undefined`) so partial data produces a valid document with `[TBD]` markers rather than a render error.

### `cpm_rpa` Python package

The skill ships a Python package at `scripts/cpm_rpa/`:

| Module | Responsibility |
|---|---|
| `config.py` | All constants and defaults (paths) |
| `schema.py` | Load and query `rpa-methodology.yaml` |
| `renderer.py` | Jinja2 render template → output document |
| `parser.py` | Extract named blocks from generated documents |
| `cli.py` | `typer` CLI: `render <artefact>` and `parse <file>` |

The CLI is invoked from the user's project root with skill-relative paths:

```
uv run --with pyyaml --with jinja2 --with typer \
  python .claude/skills/uipath-rpa-design/scripts/cpm_rpa/cli.py render pdd
```

All skill-internal paths are resolved via `Path(__file__).resolve()` in `config.py` and survive installation into any user project directory.

## Default file convention

The user works in a single project directory. All input, model, and output files default to `./docs/`:

- `./docs/project-data.yaml` — model
- `./docs/pdd.md`, `./docs/sdd.md`, … — generated outputs

The `--output` and `--data` flags override defaults when needed.

## Consequences

- Every new structured section in a template requires: a `model:` entry in the relevant topic, a snippet file at `assets/templates/snippets/<field>.md` with the Jinja2 rendering logic, and a `<!-- #region field -->` block in the relevant main template
- Human edits to generated documents are preserved across re-renders only if the edit is inside a `<!-- begin/end -->` block; edits outside are overwritten on next render
- The LLM interview must write its collected answers to `project-data.yaml` — it is not the document author; it is a data collector
