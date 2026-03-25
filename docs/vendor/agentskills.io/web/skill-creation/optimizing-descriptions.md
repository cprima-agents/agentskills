# Optimizing skill descriptions

> How to improve your skill's description so it triggers reliably on relevant prompts.

A skill only helps if it gets activated. The `description` field is the primary mechanism agents use to decide whether to load a skill.

## How skill triggering works

At startup agents load only `name` + `description` — just enough to decide when a skill might be relevant. The description carries the entire burden of triggering.

Note: agents typically only consult skills for tasks requiring knowledge beyond what they can handle alone. Simple one-step requests may not trigger a skill even if the description matches.

## Writing effective descriptions

- **Use imperative phrasing:** "Use this skill when..." rather than "This skill does..."
- **Focus on user intent, not implementation**
- **Err on the side of being pushy:** list contexts explicitly, including "even if they don't explicitly mention X"
- **Keep it concise:** a few sentences; hard limit is 1024 characters

## Designing trigger eval queries

Aim for ~20 queries: 8-10 should-trigger, 8-10 should-not-trigger.

```json
[
  { "query": "I've got a spreadsheet in ~/data/q4_results.xlsx — can you add a profit margin column?", "should_trigger": true },
  { "query": "whats the quickest way to convert this json file to yaml", "should_trigger": false }
]
```

**Should-trigger queries — vary along:**
- Phrasing (formal, casual, typos)
- Explicitness (some name the domain, some describe the need obliquely)
- Detail (terse vs. context-heavy)
- Complexity (single-step vs. multi-step)

**Should-not-trigger queries — use near-misses:**

Weak (too easy): `"Write a fibonacci function"`, `"What's the weather today?"`

Strong near-misses for a CSV analysis skill:
- `"I need to update the formulas in my Excel budget spreadsheet"` — involves spreadsheets but needs Excel editing, not CSV analysis
- `"write a python script that reads a csv and uploads each row to postgres"` — involves CSV but the task is ETL, not analysis

## Testing whether a description triggers

A query "passes" if:
- `should_trigger: true` and the skill was invoked, or
- `should_trigger: false` and the skill was not invoked

Run each query multiple times (3 is a reasonable start). Compute a **trigger rate**: fraction of runs the skill was invoked.

Trigger rate threshold: 0.5 is a reasonable default.

## Avoiding overfitting

Split your query set:
- **Train set (~60%)**: use to identify failures and guide improvements
- **Validation set (~40%)**: hold out; only use to check generalisation

## The optimization loop

1. Evaluate on train and validation sets
2. Identify train set failures (should-trigger misses, should-not-trigger false positives)
3. Revise the description — generalize, don't add specific keywords from failed queries
4. Repeat until train set passes or improvement stalls
5. Select best iteration by validation pass rate

Five iterations is usually enough.

## Applying the result

```yaml
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

## Next steps

- [Evaluating skill output quality](evaluating-skills.md)

---

*Source: https://agentskills.io/skill-creation/optimizing-descriptions.md — crawled 2026-03-25*
