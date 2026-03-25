# agentskills — task runner
# Requires: just (https://github.com/casey/just), uv

_default:
    @just --list

# Install / update the dev environment
sync:
    uv sync

# Lint all skills
lint:
    uv run ruff check skills/

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

# --- uips-log-parser ---

# Run the log parser (pass args after --)
# Usage: just log-parse -- --last 3 --errors-only
log-parse *ARGS:
    uv run skills/uips-log-parser/scripts/parse_logs.py {{ARGS}}
