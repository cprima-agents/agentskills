"""
detect — read project.json and print shell-sourceable environment variables.

Output (stdout, KEY=value lines, eval-safe):
  DOTNET=net6          (or net8 for v25+)
  ASSEMBLY=Name.Core
  CONFIG=Data/Config.xlsx

Exit 1 if project.json is missing or UiPath.System.Activities <= v21.
"""

import json
import re
import sys
from glob import glob
from pathlib import Path


def run() -> None:
    proj = Path("project.json")
    if not proj.exists():
        print("ERROR: project.json not found in current directory.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(proj.read_text(encoding="utf-8"))
    deps = data.get("dependencies", {})
    sys_act = deps.get("UiPath.System.Activities", "[22")

    m = re.search(r"\[(\d+)", sys_act)
    if not m:
        print(f"ERROR: cannot parse UiPath.System.Activities version: {sys_act}", file=sys.stderr)
        sys.exit(1)

    major = int(m.group(1))
    if major <= 21:
        print(
            f"ERROR: UiPath.System.Activities {sys_act} (v21 and below) is not supported.",
            file=sys.stderr,
        )
        sys.exit(1)

    dotnet = "net8" if major >= 25 else "net6"
    assembly = data.get("name", "Project") + ".Core"

    configs = sorted(glob("Data/Config*.xlsx"))
    if not configs:
        print("ERROR: no Data/Config*.xlsx found.", file=sys.stderr)
        sys.exit(1)
    config = configs[0]

    print(f"DOTNET={dotnet}")
    print(f"ASSEMBLY={assembly}")
    print(f"CONFIG={config}")
