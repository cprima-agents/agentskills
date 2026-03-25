---
name: uips-conform-mold
description: >
  Generate a typed C# CodedConfig class and a UiPath clipboard snippet from a
  REFramework Config.xlsx. Use when a developer wants to replace
  dictionary-based settings lookups with strongly-typed C# properties in a
  UiPath REFramework project. Triggers on: typed config, CodedConfig,
  ConFormMold, Config.xlsx to class, typed settings, REFramework config,
  InitAllSettings typed, strongly-typed config.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv. Input must be a UiPath Config.xlsx with Name/Value column headers per sheet.
metadata:
  author: cprima
  version: "0.1.0"
allowed-tools: Bash
---

# UiPath REFramework — Typed Config Class Generator

Automates tasks 1 and 4 of the integration workflow. Tasks 2–10 require
manual action in UiPath Studio and must be handed off to the user.

## Automated tasks (agent executes)

### Task 1 — Generate Config.cs

```bash
uv run skills/uips-conform-mold/scripts/conform_mold.py Data/Config.xlsx \
    --generate-tostring
```

C# is written to stdout. Redirect or copy to `Lib/Config.cs` in the project.

### Task 4 — Generate XAML clipboard snippet

```bash
uv run skills/uips-conform-mold/scripts/conform_mold.py Data/Config.xlsx \
    --generate-tostring \
    --output-xaml LoadTypedConfig.xaml
```

File is written as UTF-8 (no BOM). User must open in Notepad, Ctrl+A, Ctrl+C
before pasting into Studio — do not copy from terminal or chat output.

## Manual tasks (hand off to user)

After running the script, instruct the user to perform these steps in order
in UiPath Studio:

| # | Task | Where |
|---|---|---|
| 2 | Copy `Config.cs` → `Lib/Config.cs` | File system |
| 3 | Open project in Studio | Studio auto-adds `UiPath.CodedWorkflows` to `project.json` |
| 5 | Paste XAML snippet at bottom of "Initialize All Settings" Sequence | `Framework/InitAllSettings.xaml` |
| 6 | Import namespace `Cpmf.Config` | Studio Imports panel |
| 7 | Promote `out_ConFigTree` from local variable to `OutArgument(cc:CodedConfig)` | `Framework/InitAllSettings.xaml` |
| 8 | Declare typed receiver variable `ConFigTree` at parent TestCase sequence scope | `Tests/TestCase_InitAllSettings.xaml` |
| 9 | Wire `out_ConFigTree` into `InvokeWorkflowFile.Arguments` | `Tests/TestCase_InitAllSettings.xaml` |
| 10 | Add `VerifyExpression` assertions for object identity and typed properties | `Tests/TestCase_InitAllSettings.xaml` |

## Key CLI flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--output-xaml PATH` | — | Write ClipboardData XAML snippet to file |
| `--generate-tostring` | off | Add `ToString()` override to each class |
| `--generate-tojson` | off | Add `ToJson()` / `FromJson()` helpers |
| `--readonly` | off | Use `{ get; init; }` instead of `{ get; set; }` |
| `--no-loader` | off | Suppress `FromDataTable` / `Load()` methods |
| `--uipath-var NAME` | `out_ConFigTree` | Variable name used in the XAML snippet |

## Gotchas

- Paste the XAML from the **file** via Notepad — not from terminal or chat output. Extra characters before `<?xml` cause Studio to reject the paste.
- Task 3 (opening in Studio) must happen before task 5 (paste) so `UiPath.CodedWorkflows` is present.
- Task 6 (namespace import) must happen before task 7 (type promotion) so Studio can resolve `cc:CodedConfig`.
- `[WARN]` on stderr means a sheet had an unrecognised header row; output is still generated best-effort.
