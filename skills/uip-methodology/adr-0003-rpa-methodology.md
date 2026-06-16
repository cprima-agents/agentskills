# ADR-0003 — rpa-methodology.yaml as the skill's canonical schema

**Status:** Accepted

## Context

The skill needs a single machine-readable file that defines:
- which document types (artefacts) exist in the RPA project lifecycle
- which topics of knowledge must be captured, and by whom
- a data model describing the fields each topic contributes to generated documents

Early versions called this file `artefact-correlation.yaml` and used a `correlation:` top-level key. The file also carried a `projects:` registry mapping project slugs to local file paths — a project-specific concern that does not belong in a distributable skill.

## Decision

The file is named `rpa-methodology.yaml` and has three top-level keys:

### `artefacts:`
A list of document types the methodology recognises. Each entry carries:
- `id` — machine identifier used as YAML key throughout the file
- `label` — human display name
- `file_glob` — pattern used by the parser to locate the file in `./docs/`

### `topics:`
Formerly `correlation:`. Each entry defines one unit of knowledge:
- `topic` — human name
- `question` — elicitation prompt for the interview workflow
- `review_prompt` (optional) — quality criteria for coverage assessment, not just presence
- `model` (optional) — data model fields contributed by this topic (see below)
- Per-artefact ownership/role entries (`pdd: { owns: true, required: true }`, etc.)

The key rename from `correlation:` to `topics:` reflects actual meaning: these are knowledge areas the methodology tracks, not statistical correlations.

### `model:` blocks within topics
Each topic that produces structured output declares the field names and types the generator and parser will use. This is the contract between the interview (which populates the fields) and the Jinja2 templates (which consume them). Field names in `model:` are the same identifiers used as Jinja2 variables in templates and as `<!-- begin: field_name -->` block names in generated documents.

## What was explicitly excluded

- **`projects:` key** — project-specific file path registries do not belong in a distributable skill. Each user's project manages its own file layout under `./docs/`.
- **`coverage_map` as a lifecycle artefact** — coverage assessment is a tool that can be run at any time, not a document produced at a specific lifecycle stage. It remains a topic ("Coverage assessment") but owns no artefact.

## Consequences

- `assess.py` and `cpm_rpa/schema.py` read `schema["topics"]` (not `schema["correlation"]`)
- The parser resolves source files via `artefacts[].file_glob` rather than a project registry
- Adding a new topic requires: a `topics:` entry in this file, a `model:` block if structured output is needed, a snippet file at `assets/templates/snippets/<field>.md` with the Jinja2 rendering logic, and a `<!-- #region field -->` block in the relevant main template
