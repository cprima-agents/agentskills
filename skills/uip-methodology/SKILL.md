---
name: uip-methodology
description: >
  UiPath RPA project design skill — guides BA, Solution Architect, and PM through
  authoring and amending all project artefacts: PDD, SDD, Architecture Review,
  Estimation, ROI, TDD, DSD, Glossary. Three workflows: (A) Guided Interview —
  full structured elicitation driven by rpa-methodology.yaml, produces any
  artefact; (B) PDD Creation — focused section-by-section PDD authoring for BAs;
  (C) SDD Creation / Amendment — infers architecture decisions from PDD, patches
  existing SDDs idempotently. Trigger phrases: "start interview", "guided interview",
  "interview me", "help me document this process", "create a PDD", "fill out a PDD",
  "start a PDD", "document a process for RPA", "create an SDD", "design the solution",
  "generate SDD", "amend SDD", "update SDD", "fill in the PDD", "let's do the arch
  review", or when a PDD is available and the next step is technical design.
license: Apache-2.0
compatibility: Windows, macOS, Linux (requires Python 3.11+, uv)
metadata:
  author: Christian Prior-Mamulyan
  version: 0.1.0
allowed-tools: [shell]
---

# UiPath RPA Design

## Decision tree — pick a workflow in 3 seconds

```
Has a PDD already?
  NO  → is the user a BA or asking how to document a process?
          YES → Workflow B (PDD Creation)
          NO  → Workflow A (Guided Interview)
  YES → does an SDD exist?
          NO  → Workflow C, Create mode
          YES → Workflow C, Amend mode
```

**Default artefact order** (one per project milestone, in sequence):

```
PDD  →  SDD  →  TDD  →  estimation  →  arch-review
```

Each artefact is a prerequisite for the next. Never skip forward unless the user
explicitly asks. Offer the next artefact at the end of each workflow output.

**Hard routing rules — no interpretation required:**

| If the user says … | Do this |
| --- | --- |
| "create / fill out a PDD" or is a BA describing a process | **Workflow B** |
| "create an SDD" / "design the solution" / provides a PDD | **Workflow C, Create mode** |
| "amend / update / fix the SDD" / provides an existing SDD | **Workflow C, Amend mode** |
| "what next?" after a PDD | Say: next step is the SDD; offer Workflow C |
| "what next?" after an SDD | Say: next step is the TDD, then estimation, then arch-review |
| "start interview" / role unclear / no artefacts yet | **Workflow A** |

---

## Workflow A — Guided Interview

Conducts a staged elicitation interview that builds toward one target artefact at a
time. Driven by `references/rpa-methodology.yaml`.

### Bootstrap (always run first)

Ask these four things in one message:

1. **Project identifier** — "What short slug should I use for this project?
   (lowercase, hyphens only — e.g. `invoice-processing`, `ppo-objection`)"
2. **Process identity** — "In one sentence: what does this process do,
   from trigger to outcome?"
3. **Your role** — "What is your role on this project?"
   (Process Owner / BA / Solution Architect / Developer / PM)
4. **Target artefact and stage** — "Which document are we working toward,
   and is this a fresh start or a continuation?"

Derive from answers:
- `project_slug` — validated: lowercase, hyphens, no spaces; derive from process name if skipped
- `process_identity` — anchor sentence used to contextualise all questions
- `stage` — one of: `pdd | arch_chapter | estimation | roi | sdd | tdd | dsd | glossary | project_plan`
- `interviewer_role` — depth signal

### Scaffold (run immediately after bootstrap)

Check whether `./docs/` exists. If not, create it and tell the user. If it already
exists, confirm its location and continue.

The user works in a single project directory — all input, model, and output files
live under `./docs/`. No sub-project nesting.

### Harvest (run after scaffold; skip if day zero)

Read all files in `./docs/`. Build a coverage map:

```
topic → covered | partial | unknown | conflicting
```

For each topic record: `source` (which file), `confidence` (high / low).
If `./docs/` is empty or contains no recognisable artefacts → all topics `unknown`; skip to Interview.

### Interview Loop

Load `references/rpa-methodology.yaml`. For the active `stage`:

1. **Own topics** — where `<stage>.owns: true` → ask fully
2. **Reference topics** — where `<stage>` has `role` but no `owns` → verify briefly
3. **Absent topics** — not present for this stage → accept as forward observations only

Order: `required: true` own topics first, then optional own topics, then reference topics.

**Per own topic:** state coverage status if partial/conflicting; ask the `question` from
the YAML; follow up once on required incomplete topics; confirm before moving on.

**Per reference topic:** one line — "For [topic] — [brief restatement of known answer]
— anything to add or correct?"

**Forward observations:** when the interviewee mentions something belonging to a
different stage, capture as:
```
[FORWARD → <stage> / <topic> / section <n>]: <note>
```

### Output

After all required own topics are covered:

1. Present the **coverage summary** (covered / partial / unknown per topic)
2. List all **forward observations** grouped by target stage
3. Ask: "Shall I generate the [target artefact] draft now, or continue?"
4. If confirmed: load the matching template from `assets/templates/`, fill every section
   where answers were collected, mark uncovered sections `[TBD]`, write to
   `projects/<project_slug>/`

### Modes at a glance

| Situation | Scaffold | Harvest? | Interview mode |
| --- | --- | --- | --- |
| No artefacts exist (day zero) | create folders | skip | full greenfield — all own topics |
| Prior artefacts exist | confirm folder | yes → coverage map | gaps only |
| Resuming interrupted session | confirm folder | yes | remaining gaps |

---

## Workflow B — PDD Creation

Guide a Business Analyst through filling out a PDD interactively. Work through
sections sequentially.

### 0. Start
Ask for the **process name** and **your name / role** (BA). Confirm the output
filename: `<process-name-kebab>-pdd.md`.

### 1. Section by section
Work through the 5 PDD sections in order. For each section:
- Ask the questions from [references/elicitation-questions.md](references/elicitation-questions.md)
- Accept partial answers — mark unanswered fields `[TBD]`
- After each section, summarise what was captured and ask "Anything to add or correct before we continue?"

**Section order:**
1. Introduction (Purpose, Objectives, Key Contacts, Prerequisites)
2. AS-IS Process Description (Overview, Applications, Process Map, Steps, Input Data)
3. TO-BE Process Description (Scope, Exceptions, Reporting)
4. Other Observations
5. Additional Documentation

### 2. Write the file
Load `assets/templates/pdd-template.md`, substitute all captured values, and write
to `projects/<slug>/<process-name-kebab>-pdd.md`.

### 3. Finish
Tell the user the output path. List any `[TBD]` items remaining and suggest they
resolve them before handing the PDD to a Solution Architect.

### Rules
- Never invent business rules, volumes, or exception behaviour — always ask.
- Ask at most 4–5 questions per message.
- Use plain business language, not UiPath jargon.
- If the user says "skip" or "I don't know", mark the field `[TBD]` and move on.
- Prefer tables and bullet lists when summarising captured data back to the user.

---

## Workflow C — SDD Creation / Amendment

Guide a Solution Architect through producing or completing an SDD. Infer as much
as possible from the PDD; ask only for decisions that cannot be derived from it.
**Idempotent** — safe to run repeatedly against an existing SDD.

### 0. Start — detect mode

Ask for the PDD (file path or reference to an already-loaded file).

Check whether an SDD already exists:
- **No SDD found** → **Create mode**: proceed from step 1.
- **SDD found** → **Amend mode**: jump to step A.

Confirm the output filename: `<process-name-kebab>-sdd.md`.

---

### Create path

### 1. Extract PDD data
Read the full PDD and extract:
- Process name, department, schedule, volume, peak volume
- Applications list (names, client type, access method)
- In-scope / out-of-scope steps
- Known business and application exceptions
- Reporting requirements

### 2. Apply inference rules
Load [references/inference-rules.md](references/inference-rules.md) and derive as many
SDD fields as possible. Summarise inferences in a short table for the architect to review:

| Field | Inferred Value | Confidence | Reason |
| --- | --- | --- | --- |
| Framework | REFramework | High | Queue-based transactional, >50 items/day |
| Robot Type | BOR | High | No human interaction required |
| … | … | … | … |

### 3. Ask for gaps only
For fields that cannot be inferred, ask the architect. Load
[references/gap-questions.md](references/gap-questions.md) for the question set.
Group related questions to max 5 per message.

### 4. Build project structure
Apply decomposition heuristics from [references/inference-rules.md](references/inference-rules.md)
to define the project list and workflow inventory. Present for confirmation before writing.

### 5. Write the file
Load `assets/templates/sdd-template.md`, substitute all values, and write to
`projects/<slug>/<process-name-kebab>-sdd.md`.

Section 9 is an estimation reference stub — fill in the four summary rows only if data
is available. Effort detail lives in a separate `<process-name>-estimation.md`; do not
inline it in the SDD.

### 6. Finish
Report the output path. List any `[SME REVIEW]` items remaining. Suggest next steps:
hand-off to TDD author, generate `<process-name>-estimation.md` from
`assets/templates/estimation-template.md`, open UiPath Studio project.

---

### Amend path

### A. Inventory the existing SDD
Read the full SDD. Produce a gap inventory:

| Section | Status | Gap |
| --- | --- | --- |
| 3.1 Design Decisions | complete | — |
| 4.1 Dispatcher config | partial | Trigger/schedule is [TBD] |
| 8.1 System Access Prerequisites | partial | Owner and status columns incomplete |
| … | … | … |

Gap signals (in priority order):
1. `[TBD]` — value deferred
2. `[SME REVIEW]` — needs business owner decision
3. `[DEFAULT]` — placeholder to confirm
4. Open questions in section 10 still marked Open
5. Sections present in `assets/templates/sdd-template.md` but missing from this SDD
6. Data inconsistencies (e.g. payback figure differs from estimation file)

### B. Resolve from PDD and inference rules
Read the PDD. Load [references/inference-rules.md](references/inference-rules.md).
For each gap, attempt to resolve without asking. Mark resolved gaps with the source.

### C. Ask for remaining gaps only
For gaps that cannot be resolved, ask the architect. Group related questions to max 5
per message.

### D. Patch the file
Edit the existing SDD in place. Only modify cells/sections with identified gaps.
Do not reformat, reorder, or rewrite sections that are already complete.

### E. Finish
Report what was changed. List any `[SME REVIEW]` items still open. Note open
questions in section 10 that are now resolved vs. still open.

---

## Shared Rules

- Never invent selectors, UI element identifiers, or field names — mark as `[DEV: inspect at build time]`.
- Use `[DEFAULT]` for industry-standard values (retry=3, timeout=30s, queue item deadline=24h).
- Use `[SME REVIEW]` for gaps requiring business knowledge not covered by PDD or inference rules.
- Do not copy PDD sections verbatim into an SDD — reorganise content into the SDD structure.
- The Workflow Inventory table is the most important SDD section; every PDD in-scope step must map to at least one workflow file.
- **Amend mode only**: never touch a field that already has a real value.
