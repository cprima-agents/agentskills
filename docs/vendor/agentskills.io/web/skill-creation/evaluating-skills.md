# Evaluating skill output quality

> How to test whether your skill produces good outputs using eval-driven iteration.

## Designing test cases

A test case has three parts:
- **Prompt**: a realistic user message
- **Expected output**: a human-readable description of success
- **Input files** (optional)

Store in `evals/evals.json`:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"]
    }
  ]
}
```

**Tips:**
- Start with 2-3 test cases
- Vary phrasing (formal, casual, with typos)
- Vary explicitness (some name the domain, some describe the need without naming it)
- Cover edge cases (malformed input, unusual requests)

## Workspace structure

```
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json
```

Run each test case both **with the skill** and **without** (baseline). Each run should start with a clean context.

## Writing assertions

Add after seeing first results. Good assertions:
- `"The output file is valid JSON"` — programmatically verifiable
- `"The bar chart has labeled axes"` — specific and observable
- `"The report includes at least 3 recommendations"` — countable

Weak: `"The output is good"`, `"Uses exactly the phrase X"` (too brittle)

```json
"assertions": [
  "The output includes a bar chart image file",
  "The chart shows exactly 3 months",
  "Both axes are labeled",
  "The chart title or caption mentions revenue"
]
```

## Grading outputs

Record **PASS** or **FAIL** with specific evidence quoting the output:

```json
{
  "assertion_results": [
    {
      "text": "Both axes are labeled",
      "passed": false,
      "evidence": "Y-axis is labeled 'Revenue ($)' but X-axis has no label"
    }
  ],
  "summary": { "passed": 3, "failed": 1, "total": 4, "pass_rate": 0.75 }
}
```

**Grading principles:**
- Require concrete evidence for a PASS — don't give benefit of the doubt
- Review the assertions themselves for quality (too easy, too hard, unverifiable)

## Aggregating results

```json
{
  "run_summary": {
    "with_skill": { "pass_rate": { "mean": 0.83 }, "tokens": { "mean": 3800 } },
    "without_skill": { "pass_rate": { "mean": 0.33 }, "tokens": { "mean": 2100 } },
    "delta": { "pass_rate": 0.50, "tokens": 1700 }
  }
}
```

## Analyzing patterns

- Remove assertions that always pass in both configurations (no signal)
- Investigate assertions that always fail in both (broken assertion or too hard)
- Study assertions that pass with skill but fail without (where skill adds value)
- Tighten instructions when results are inconsistent across runs

## Iterating on the skill

After grading and human review, three signal sources:
1. **Failed assertions** → specific gaps in instructions
2. **Human feedback** → broader quality issues
3. **Execution transcripts** → *why* things went wrong

Give all three + current `SKILL.md` to an LLM and ask it to propose changes.

**Iteration guidelines:**
- Generalize from feedback (don't add narrow patches)
- Keep the skill lean (fewer, better instructions)
- Explain the why (reasoning-based > rigid directives)
- Bundle repeated work into `scripts/`

### The loop

1. Propose improvements from eval signals
2. Apply changes
3. Rerun in new `iteration-<N+1>/` directory
4. Grade and aggregate
5. Human review → repeat

Stop when satisfied, feedback is consistently empty, or improvement stalls.

---

*Source: https://agentskills.io/skill-creation/evaluating-skills.md — crawled 2026-03-25*
