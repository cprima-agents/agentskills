"""Shared paths and defaults for the RPA document tooling.

These values are used by both the CLI commands and the low-level helpers so
the package behaves the same whether it is run from the repo or installed.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Skill-internal paths. Resolve relative to this file so imports keep working
# after the package is copied into another environment.
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent  # scripts/cpm_rpa/
SKILL_ROOT = _HERE.parent.parent  # uipath-rpa-design/
TEMPLATES_DIR = SKILL_ROOT / "assets" / "templates"
DEFAULT_SCHEMA = SKILL_ROOT / "references" / "rpa-methodology.yaml"

# ---------------------------------------------------------------------------
# User-project defaults. These stay relative to the caller's working directory
# because the generated docs are written into the active project.
# ---------------------------------------------------------------------------

DEFAULT_DOCS = Path("docs")
DEFAULT_DATA = DEFAULT_DOCS / "project-data.yaml"

__all__ = ["DEFAULT_DOCS", "DEFAULT_DATA", "DEFAULT_SCHEMA", "SKILL_ROOT", "TEMPLATES_DIR"]
