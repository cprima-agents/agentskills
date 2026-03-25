---
name: uips-log-parser
description: >
  Parse and analyse UiPath Studio local execution logs to diagnose automation
  runs. Use when a developer asks about errors, warnings, duration, or status of
  a UiPath process run; when troubleshooting a failed, interrupted, or slow
  automation; when searching for a specific message across multiple runs. Triggers
  on: UiPath log, execution log, Studio run, robot error, job failed, process
  crashed, how long did it run, find in log.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv. Log auto-discovery is Windows-only (UiPath Studio writes logs to %LOCALAPPDATA%\UiPath\Logs\).
metadata:
  author: cprima
  version: "0.1.0"
allowed-tools: Bash
---

# UiPath Studio Execution Log Parser

Parse local UiPath Studio execution logs grouped by job run (`jobId`).

## Run the script

```bash
# Last job (default)
uv run skills/uips-log-parser/scripts/parse_logs.py

# Specific file
uv run skills/uips-log-parser/scripts/parse_logs.py --file "C:/Users/<user>/Downloads/2026-03-25_Execution.log"

# Last N runs from auto-discovered logs
uv run skills/uips-log-parser/scripts/parse_logs.py --last 5

# All runs, errors only
uv run skills/uips-log-parser/scripts/parse_logs.py --all --errors-only

# Search for a string across all runs
uv run skills/uips-log-parser/scripts/parse_logs.py --all --needle "Object reference"

# Duration between two copied log lines
uv run skills/uips-log-parser/scripts/parse_logs.py --duration "LINE1" "LINE2"

# Structured output for further processing
uv run skills/uips-log-parser/scripts/parse_logs.py --last 3 --format json
```

All diagnostics go to stderr; `--format json` sends clean JSON to stdout.

## Understanding the output

Each run shows a status flag:

| Flag | Meaning |
|------|---------|
| `[ OK ]` | Execution ended normally, no errors |
| `[FAIL]` | Execution ended normally, with errors |
| `[ .. ]` | No "execution ended" message — may still be running, was interrupted, or log is truncated |

**Do not assume `[ .. ]` means failure.** The run may be active right now.

## Log auto-discovery

The script searches these locations by default:

- `%LOCALAPPDATA%\UiPath\Logs\` — Studio / attended Robot (user-level)
- `C:\ProgramData\UiPath\Logs\` — Robot service (system-level)

Use `--log-dir PATH` to override, or `--file PATH` to point at a single file.

## Key CLI flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--last N` | 1 | Show last N runs |
| `--all` | off | Show all runs |
| `--days N` | 7 | Discovery lookback window |
| `--date YYYY-MM-DD` | — | Filter to one day |
| `--process NAME` | — | Filter by process name (substring) |
| `--needle TEXT` | — | Filter runs containing TEXT; highlights matches |
| `--errors-only` | off | Show only runs with errors |
| `--warnings` | off | Also show warning details |
| `--format json\|text` | text | Output format |
| `--list-files` | off | Show discovered files and exit |

## Gotchas

- Log files start with a UTF-8 BOM (`\xEF\xBB\xBF`) — the script strips it automatically.
- The `[ .. ]` status does **not** indicate a crash when the user is actively developing in Studio.
- Duration (`totalExecutionTime`) is only present on the final "execution ended" entry. If the run is open, duration will be `null` in JSON / `?` in text.
- Multiple runs per day are in the same file, separated only by `jobId`.
- The `execution_log_data/` subfolder contains a SQLite DB (cloud-synced data) — the script does not read it.
