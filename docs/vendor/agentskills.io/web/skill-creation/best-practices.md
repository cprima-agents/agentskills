# Best practices for skill creators

> How to write skills that are well-scoped and calibrated to the task.

## Start from real expertise

Effective skills are grounded in real expertise, not generic LLM output. Feed domain-specific context into the creation process.

**Extract from a hands-on task:** Complete a real task with an agent, then extract the reusable pattern. Note:
- Steps that worked
- Corrections you made (e.g., "use library X instead of Y")
- Input/output formats
- Context you provided (project-specific facts, conventions)

**Synthesize from project artifacts:** Good source material:
- Internal documentation, runbooks, style guides
- API specs, schemas, configuration files
- Code review comments and issue trackers
- Version control history, especially patches and fixes
- Real-world failure cases and resolutions

## Refine with real execution

Run the skill against real tasks, then feed all results back into the creation process. Even one pass of execute-then-revise noticeably improves quality.

Read agent execution traces, not just final outputs — wasted steps reveal vague instructions, misapplied instructions, or too many options without a clear default.

## Spending context wisely

### Add what the agent lacks, omit what it knows

Focus on project-specific conventions, domain-specific procedures, non-obvious edge cases. Skip explanations of general concepts the agent already knows.

```markdown
<!-- Too verbose -->
PDF (Portable Document Format) files are a common file format...
Use pdfplumber because it handles most cases well.

<!-- Better -->
Use pdfplumber for text extraction. For scanned documents, fall back to
pdf2image with pytesseract.
```

### Design coherent units

Scope a skill to a coherent unit of work — too narrow forces multiple skills per task; too broad makes precise activation hard.

### Keep SKILL.md under 500 lines

Move detailed reference material to `references/`. Tell the agent *when* to load each file:

> "Read `references/api-errors.md` if the API returns a non-200 status code"

## Calibrating control

### Match specificity to fragility

**Give freedom** when multiple approaches are valid — explain *why* rather than rigid directives.

**Be prescriptive** when operations are fragile or a specific sequence must be followed:

```markdown
## Database migration

Run exactly this sequence:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
```

### Provide defaults, not menus

Pick a default and mention alternatives briefly:

```markdown
<!-- Too many options -->
You can use pypdf, pdfplumber, PyMuPDF, or pdf2image...

<!-- Clear default with escape hatch -->
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Favor procedures over declarations

Teach the agent *how to approach* a class of problems, not what to produce for one specific instance.

## Patterns for effective instructions

### Gotchas sections

Highest-value content — concrete corrections to mistakes the agent will make without being told:

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL`.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
```

When an agent makes a mistake you correct, add it to gotchas.

### Templates for output format

Provide a concrete template rather than describing the format in prose:

```markdown
## Report structure

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with supporting data

## Recommendations
1. Specific actionable recommendation
```
```

### Checklists for multi-step workflows

```markdown
## Form processing workflow

- [ ] Step 1: Analyze the form (`scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (`fields.json`)
- [ ] Step 3: Validate mapping (`scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (`scripts/fill_form.py`)
- [ ] Step 5: Verify output (`scripts/verify_output.py`)
```

### Validation loops

```markdown
1. Make your edits
2. Run validation: `python scripts/validate.py output/`
3. If validation fails, fix issues and run again
4. Only proceed when validation passes
```

### Plan-validate-execute

For batch or destructive operations: create an intermediate plan, validate against a source of truth, then execute.

## Next steps

- [Evaluating skill output quality](evaluating-skills.md)
- [Optimizing skill descriptions](optimizing-descriptions.md)

---

*Source: https://agentskills.io/skill-creation/best-practices.md — crawled 2026-03-25*
