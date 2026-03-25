"""
patch_project — add a dependency to project.json if absent.

Default: adds UiPath.CodedWorkflows [24.10.1].
Idempotent. Prints what it did.
"""

import json
import sys
from pathlib import Path


def run(package: str, version: str) -> None:
    proj = Path("project.json")
    if not proj.exists():
        print("ERROR: project.json not found in current directory.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(proj.read_text(encoding="utf-8"))
    deps = data.setdefault("dependencies", {})

    if package in deps:
        print(f"Already present: {package} {deps[package]}")
        return

    deps[package] = f"[{version}]"
    proj.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Added {package} [{version}]")
