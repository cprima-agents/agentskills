# Using scripts in skills

> How to run commands and bundle executable scripts in your skills.

## One-off commands

When an existing package does what you need, reference it directly in `SKILL.md`:

| Tool | Example | Notes |
|------|---------|-------|
| `uvx` | `uvx ruff@0.8.0 check .` | Python; fast caching; requires uv |
| `pipx` | `pipx run 'black==24.10.0' .` | Python; mature alternative to uvx |
| `npx` | `npx eslint@9 --fix .` | Node.js; bundled with npm |
| `bunx` | `bunx eslint@9 --fix .` | Bun environments |
| `deno run` | `deno run npm:eslint@9 -- --fix .` | Deno; requires permission flags |
| `go run` | `go run golang.org/x/tools/cmd/goimports@v0.28.0 .` | Go; built-in |

**Tips:**
- Pin versions for reproducibility
- State prerequisites in `SKILL.md` or use the `compatibility` frontmatter field
- Move complex commands into `scripts/` when they're hard to get right inline

## Referencing scripts from `SKILL.md`

Use relative paths from the skill directory root:

```markdown
## Available scripts

- **`scripts/validate.sh`** — Validates configuration files
- **`scripts/process.py`** — Processes input data

## Workflow

1. Run validation:
   ```bash
   bash scripts/validate.sh "$INPUT_FILE"
   ```

2. Process results:
   ```bash
   python3 scripts/process.py --input results.json
   ```
```

## Self-contained scripts

Bundle scripts in `scripts/` with inline dependency declarations:

**Python (PEP 723) — run with `uv run`:**

```python
# /// script
# dependencies = [
#   "beautifulsoup4",
# ]
# ///

from bs4 import BeautifulSoup
...
```

```bash
uv run scripts/extract.py
```

**Deno:**

```typescript
import * as cheerio from "npm:cheerio@1.0.0";
```

```bash
deno run scripts/extract.ts
```

**Bun:**

```typescript
import * as cheerio from "cheerio@1.0.0";
```

```bash
bun run scripts/extract.ts
```

## Designing scripts for agentic use

### Avoid interactive prompts (hard requirement)

Agents operate in non-interactive shells — any TTY prompt will hang indefinitely. Accept all input via flags, env vars, or stdin.

```
# Bad: hangs waiting for input
$ python scripts/deploy.py
Target environment: _

# Good: clear error
$ python scripts/deploy.py
Error: --env is required. Options: development, staging, production.
```

### Document usage with `--help`

```
Usage: scripts/process.py [OPTIONS] INPUT_FILE

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --output FILE      Write output to FILE instead of stdout
  --verbose          Print progress to stderr
```

### Write helpful error messages

```
Error: --format must be one of: json, csv, table.
       Received: "xml"
```

### Use structured output

Prefer JSON, CSV, TSV over free-form text. Send structured data to **stdout**, diagnostics to **stderr**.

### Further considerations

- **Idempotency** — agents may retry; "create if not exists" is safer than "create and fail on duplicate"
- **Dry-run support** — `--dry-run` flag for destructive operations
- **Meaningful exit codes** — document different failure types
- **Safe defaults** — require explicit confirmation flags (`--confirm`, `--force`) for destructive ops
- **Predictable output size** — default to a summary or limit; support `--offset` for pagination; require `--output FILE` for large outputs

---

*Source: https://agentskills.io/skill-creation/using-scripts.md — crawled 2026-03-25*
