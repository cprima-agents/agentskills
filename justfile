# agentskills — task runner
# Requires: just (https://github.com/casey/just), uv

set windows-shell := ["pwsh", "-NoLogo", "-Command"]

_py       := "uv run python"
_uip      := "skills/uip-methodology"
_scripts  := _uip + "/scripts"
_tpls     := _uip + "/assets/templates"

_default:
    @just --list

# Install / update the dev environment
sync:
    uv sync

# Lint all skills
lint:
    uv run ruff check skills/

# Auto-fix lint violations
lint-fix:
    uv run ruff check --fix skills/

# Format all skills
fmt:
    uv run ruff format skills/

# Lint + format check (CI-safe, no writes)
check:
    uv run ruff check skills/
    uv run ruff format --check skills/

# Run tests
test:
    uv run pytest

# ── folder-harvest ─────────────────────────────────────────────────────────────

# Harvest files from one or more folders into <name>_harvested/ siblings
# Usage: just harvest path/to/folder [-- --hint path/to/folder=label --dry-run]
harvest *ARGS:
    uv run skills/folder-harvest/scripts/harvest.py {{ARGS}}

# ── uips-log-parser ────────────────────────────────────────────────────────────

# Run the log parser (pass args after --)
# Usage: just log-parse -- --last 3 --errors-only
log-parse *ARGS:
    uv run skills/uips-log-parser/scripts/parse_logs.py {{ARGS}}

# ── uip-methodology: methodology queries ───────────────────────────────────────

# List all defined artefacts with file globs and flags
artefacts:
    {{_py}} {{_scripts}}/methodology.py artefacts

# List all topics
topics:
    {{_py}} {{_scripts}}/methodology.py topics

# List topics present in an artefact  (e.g.: just topics-in sdd)
topics-in artefact:
    {{_py}} {{_scripts}}/methodology.py topics --artefact {{artefact}}

# List all topics that have a concept.model
models:
    {{_py}} {{_scripts}}/methodology.py models

# Dump the full YAML definition for one topic  (e.g.: just topic "container arch")
topic name:
    {{_py}} {{_scripts}}/methodology.py topic "{{name}}"

# Show model fields for one topic  (e.g.: just model "component arch")
model topic:
    {{_py}} {{_scripts}}/methodology.py model "{{topic}}"

# Show which topics appear in an artefact with section + template  (e.g.: just coverage arch_review)
coverage artefact="":
    {{_py}} {{_scripts}}/methodology.py coverage {{artefact}}

# List every <!-- #region X --> found across all templates with their artefact
regions:
    {{_py}} {{_scripts}}/methodology.py regions

# Glue table — semantics, acquisition, transforms for all topics
glue:
    {{_py}} {{_scripts}}/methodology.py glue

# Glue detail for one topic  (e.g.: just glue-topic "architecture decision")
glue-topic topic:
    {{_py}} {{_scripts}}/methodology.py glue "{{topic}}"

# Elicitation questions for an artefact  (e.g.: just interview pdd)
interview artefact="pdd":
    {{_py}} {{_scripts}}/methodology.py interview --artefact {{artefact}}

# List all named enums
enums:
    {{_py}} {{_scripts}}/methodology.py enums

# Show one enum's values  (e.g.: just enum adr_status)
enum name:
    {{_py}} {{_scripts}}/methodology.py enums {{name}}

# ── uip-methodology: outline ───────────────────────────────────────────────────

# Outline all templates at depth 2
outline:
    {{_py}} {{_scripts}}/outline.py --depth 2

# Outline a named template at given depth  (e.g.: just tpl sdd 3)
tpl name depth="2":
    {{_py}} {{_scripts}}/outline.py --depth {{depth}} {{_tpls}}/{{name}}-template.md

# Shorthand aliases
sdd depth="3": (tpl "sdd" depth)
pdd depth="3": (tpl "pdd" depth)
tdd depth="3": (tpl "tdd" depth)
arch-review depth="2": (tpl "arch-review" depth)
roi depth="2": (tpl "roi" depth)
project-plan depth="2": (tpl "project-plan" depth)

# ── uip-methodology: render ────────────────────────────────────────────────────

# Parse all source artefacts into project-data.yaml  (run once before first render)
parse-arch-review docs="docs":
    {{_py}} {{_scripts}}/cpm_rpa/cli.py parse {{docs}}/pdd.md
    {{_py}} {{_scripts}}/cpm_rpa/cli.py parse {{docs}}/sdd.md
    {{_py}} {{_scripts}}/cpm_rpa/cli.py parse {{docs}}/estimation.md
    {{_py}} {{_scripts}}/cpm_rpa/cli.py parse {{docs}}/roi.md

# Render arch-review document from project-data.yaml
render-arch-review data="docs/project-data.yaml" out="docs/arch-review.md":
    {{_py}} {{_scripts}}/cpm_rpa/cli.py render arch_review --data {{data}} --output {{out}}

# Generate ROI chart PNG from rendered arch-review
roi-chart src="docs/arch-review.md":
    {{_py}} {{_scripts}}/generate_roi_chart.py {{src}}

# Full pipeline: parse all owning artefacts, render, generate ROI chart
arch-review-full docs="docs" out="docs/arch-review.md":
    just parse-arch-review docs={{docs}}
    just render-arch-review data={{docs}}/project-data.yaml out={{out}}
    just roi-chart src={{out}}

# ── uip-methodology: coverage checks ──────────────────────────────────────────

# Check skill repo: YAML snippet refs, template regions, and orphan snippets
meth-check:
    {{_py}} {{_scripts}}/check_coverage.py templates

# Parse every owning template and check that all extracted field names are in the schema
meth-check-fields:
    {{_py}} {{_scripts}}/check_coverage.py fields

# Check project docs directory: required regions present in each artefact file
meth-check-docs docs="docs":
    {{_py}} {{_scripts}}/check_coverage.py docs {{docs}}
