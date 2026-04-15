---
name: uips-localcli
description: >
  Locate, install, and invoke uipcli.exe and UiRobot.exe for UiPath package
  operations. Use when running package pack, package analyze (Workflow Analyzer),
  or local process execution against a UiPath project. Triggers on: uipcli,
  package analyze, workflow analyzer, pack nupkg, uipath cli, run process,
  execute nupkg, UiRobot.
license: Apache-2.0
compatibility: Requires PowerShell 7+ and CpmfUipsPack PS module (auto-installed if absent). Windows only.
metadata:
  author: cprima
  version: "0.1.0"
allowed-tools: Bash
---

# UiPath Local CLI — uipcli and UiRobot

Two executables cover local UiPath operations:

| Tool | Purpose |
|---|---|
| `uipcli.exe` | Package pack and Workflow Analyzer (`package analyze`) |
| `UiRobot.exe` | Local process execution (no Orchestrator required) |

Two builds of uipcli exist — **net6 (23.x)** and **net8 (25.x)** — with
meaningfully different `package analyze` syntax. Always confirm the .NET
target with the user before proceeding.

---

## Phase 1 — Locate uipcli

The two builds are installed to different sub-paths:

| Build | Path pattern |
|---|---|
| net6 (23.x) | `~/.cpmf/tools/uipcli-23.*/extracted/tools/uipcli.exe` |
| net8 (25.x) | `~/.cpmf/tools/uipcli-25.*/uipcli.exe` |

```bash
# Check net6
ls ~/.cpmf/tools/uipcli-23.*/extracted/tools/uipcli.exe 2>/dev/null | sort -V | tail -1

# Check net8
ls ~/.cpmf/tools/uipcli-25.*/uipcli.exe 2>/dev/null | sort -V | tail -1
```

If nothing is returned → proceed to Phase 2. If found → skip to Phase 3.

---

## Phase 2 — Install via CpmfUipsPack (only if absent)

`CpmfUipsPack` (v0.2.4+) exports `Install-CpmfUipsPackCommandLineTool`.
PowerShell 7+ required.

```powershell
# Install the module (idempotent)
Install-PSResource -Name CpmfUipsPack -TrustRepository

# Check exact parameter syntax before calling install
Get-Help Install-CpmfUipsPackCommandLineTool -Full
```

> Do not guess parameter names — always read the help output first.

### Fallback — corporate / restricted environment

If `Install-PSResource` fails (network blocked, PowerShell Gallery unreachable,
corporate proxy), **do not retry automatically**. Instead, ask the user:

> The automatic install via PowerShell Gallery failed. Please provide one of:
> 1. The path to an already-extracted `uipcli.exe` on this machine, or
> 2. A `.nupkg` or `.zip` file containing uipcli that you have downloaded manually
>    (e.g. from https://www.powershellgallery.com/packages/CpmfUipsCLI or a
>    corporate artifact repository).

If the user provides a `.nupkg` or `.zip`, extract it and locate `uipcli.exe`
inside (look under `tools/` or `lib/net*/`). Set `$UIPCLI` to that path and
skip Phase 3's glob discovery.

---

## Phase 2b — Discover local NuGet feed

Run this before building a NuGet.config for `package analyze`:

```bash
dotnet nuget list source
```

Filter the output for **local (filesystem) sources** — lines whose value is a
drive-letter path or UNC path, not `http`. Example match: `C:\Users\Public\Documents\myNugetPackages`.

```bash
dotnet nuget list source | grep -E '^\s+[A-Za-z]:\\|^\s+\\\\' 
```

- **One local source found** → propose it to the user; confirm before using.
- **Multiple local sources** → list them and ask the user to pick.
- **None found** → ask the user to provide the folder path.

Once the local feed folder is confirmed, generate a minimal `NuGet.config`
(e.g. in a temp directory) to pass to `--nugetConfigFilePath`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="local-feed" value="<confirmed-local-folder>" />
    <add key="UiPath-Official" value="https://uipath.pkgs.visualstudio.com/Public.Feeds/_packaging/UiPath-Official/nuget/v3/index.json" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>
</configuration>
```

Store the path to this file as `$NUGET_CONFIG` for use in Phase 4.

---

## Phase 3 — Select binary (.NET version required from user)

**Ask the user explicitly — do not infer silently:**

> Which .NET target does this UiPath project use — **net6** or **net8**?
> Check `project.json` → `"targetFramework"` field.
> Studio 23.x and earlier → net6; Studio 24.x and later → net8.

Once confirmed:

```bash
# net8
UIPCLI=$(ls ~/.cpmf/tools/uipcli-25.*/uipcli.exe 2>/dev/null | sort -V | tail -1)

# net6
UIPCLI=$(ls ~/.cpmf/tools/uipcli-23.*/extracted/tools/uipcli.exe 2>/dev/null | sort -V | tail -1)

echo "Using: $UIPCLI"
```

---

## Phase 4 — Usage patterns

> **Getting help from uipcli:** uipcli does not support a `--help` flag at the
> top level. To see available commands and subcommand syntax, run it with no
> arguments:
> ```bash
> "$UIPCLI"
> "$UIPCLI" package
> "$UIPCLI" package analyze
> ```
> Each level prints its own usage without requiring `--help`.

### package pack (net6 and net8 — syntax identical)

```bash
"$UIPCLI" package pack "<project.json or project-folder>" \
  --output "<output-folder>"
```

Produces a `.nupkg` in `<output-folder>`.

---

### package analyze — net6 (uipcli 23.x)

```bash
"$UIPCLI" package analyze "<path/to/project.json>" \
  --analyzerTraceLevel Warning \
  --resultPath "<output.json>" \
  --traceLevel Off
```

| Flag | Notes |
|---|---|
| Positional arg | Path to `project.json` file (or folder containing one) |
| `--analyzerTraceLevel` | `Off\|Error\|Warning\|Info\|Verbose` |
| `--traceLevel` | `Off\|Error\|Warning\|Info\|Verbose` |
| `--nugetConfigFilePath` | **Not available** in net6 |
| `--governanceFilePath` | **Not available** in net6 |

---

### package analyze — net8 (uipcli 25.x)

```bash
"$UIPCLI" package analyze "<workspace-folder>" \
  --analyzerTraceLevel Warning \
  --resultPath "<output.json>" \
  --traceLevel None \
  --nugetConfigFilePath "<NuGet.config>"
```

Add `--governanceFilePath` when using a governance policy from Automation Ops:

```bash
"$UIPCLI" package analyze "<workspace-folder>" \
  --analyzerTraceLevel Warning \
  --resultPath "<output.json>" \
  --traceLevel None \
  --nugetConfigFilePath "<NuGet.config>" \
  --governanceFilePath "<governance.json>"
```

| Flag | Notes |
|---|---|
| Positional arg | Workspace **folder** path (not project.json) |
| `--analyzerTraceLevel` | Default is `Error`; use `Warning` for non-default rules |
| `--traceLevel` | `None\|Critical\|Error\|Warning\|Information\|Verbose` |
| `--nugetConfigFilePath` | Required for custom/local rule pack feeds |
| `--governanceFilePath` | Optional; governance policy file |

Result JSON format (array of violation objects):

```json
[
  {
    "ErrorCode": "CPMF-FC002",
    "FilePath": "C:\\workspace\\project",
    "ErrorSeverity": "Warning",
    "Description": "..."
  }
]
```

> **Project-level violations** have `FilePath` set to the workspace directory
> (no `.xaml` extension), not a specific workflow file.

---

### execute (local, no Orchestrator) — UiRobot.exe

Locate the newest installed version:

```bash
UIROBOT=$(ls "C:/Program Files/UiPathPlatform/Studio/"*/UiRobot.exe 2>/dev/null | sort -V | tail -1)
echo "Using: $UIROBOT"
```

Run a packed `.nupkg`:

```bash
"$UIROBOT" execute --file "<path-to.nupkg>"
```

Run with input arguments (JSON):

```bash
"$UIROBOT" execute --file "<path-to.nupkg>" \
  --input '{"argName": "value"}'
```

Run a specific entry point:

```bash
"$UIROBOT" execute --file "<path-to.nupkg>" --entry "OtherEntryPoint.xaml"
```

---

## Gotchas

| Issue | Detail |
|---|---|
| Wrong path depth | net6 binary is under `extracted/tools/`; net8 is directly in the version folder — glob patterns differ |
| No `--nugetConfigFilePath` on net6 | Custom rule packs (e.g. CPMF) cannot be loaded via NuGet config in net6 analyze — Phase 2b and `$NUGET_CONFIG` only apply to net8 |
| `--traceLevel` values differ | net6: `Off` · net8: `None` — using the wrong value may produce an error |
| `--analyzerTraceLevel Warning` required | Rules with `IsEnabledByDefault = false` are silently skipped without this flag |
| Project-level violations | `FilePath` is the workspace directory, not a `.xaml` file — do not expect a filename |
| UiRobot ≠ uipcli | uipcli has no local execute command; use `UiRobot.exe execute` for running processes locally |
