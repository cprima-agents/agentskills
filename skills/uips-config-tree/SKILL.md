---
name: ConFigTree
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
  version: "0.1.1"
allowed-tools: Bash
---

# UiPath REFramework — Typed Config Class Generator

Four phases: **Initialize** (guard + detect), **Generate** (agent runs all
file changes), **Implement** (user reloads Studio), **Finalize** (TestCase
patched automatically).

## Initialize

Verify the working directory is a REFramework project, then resolve build
variables. Abort if either file check fails.

```bash
# Both must be present — abort if either is missing
test -f Framework/InitAllSettings.xaml
ls Data/Config*.xlsx
```

| Check | Path | Absence means |
|---|---|---|
| REFramework indicator | `Framework/InitAllSettings.xaml` | Not a REFramework project — skill does not apply |
| Config input | `Data/Config*.xlsx` | Nothing to generate from — ask user for the file location |

Resolve `DOTNET`, `ASSEMBLY`, and `CONFIG` from `project.json`:

```bash
eval $(uv run config-tree detect)
echo "DOTNET=$DOTNET  ASSEMBLY=$ASSEMBLY  CONFIG=$CONFIG"
```

| `UiPath.System.Activities` | `DOTNET` |
|---|---|
| `[25.*]` | `net8` |
| `[22.*]` / `[23.*]` / `[24.*]` | `net6` |
| `[21.*]` and below | **not supported — aborts** |

## Generate

Run all of the following in order. Each step is idempotent.

```bash
# Generate Lib/Config.cs
uv run config-tree generate "$CONFIG" --generate-tostring --dotnet-version "$DOTNET" > Lib/Config.cs

# Add UiPath.CodedWorkflows to project.json if absent
uv run config-tree patch-project

# Generate LoadTypedConfig.xaml clipboard snippet
uv run config-tree generate "$CONFIG" --generate-tostring --dotnet-version "$DOTNET" --output-xaml LoadTypedConfig.xaml

# Patch Framework/InitAllSettings.xaml
uv run config-tree patch-init-settings --assembly "$ASSEMBLY" --xaml LoadTypedConfig.xaml

# Patch Tests/TestCase_InitAllSettings.xaml
uv run config-tree patch-testcase --assembly "$ASSEMBLY"
```

## Implement

Tell the user:

> Generate is complete. **Close the project and re-open it in Studio** so
> Studio restores the new `UiPath.CodedWorkflows` dependency. The workflow
> will compile and run once the package restore finishes.
>
> After re-opening, Studio will show an **"Import Arguments"** prompt on the
> `InvokeWorkflowFile` in `TestCase_InitAllSettings.xaml` — this is expected.
> The patcher has already pre-added the correct `out_ConFigTree` binding;
> clicking **Import Arguments** simply confirms it. No bindings need to be
> set manually.

## Finalize

`patch-testcase` adds to `Tests/TestCase_InitAllSettings.xaml`:

- `xmlns:cc` and `Cpmf.Config` namespace/assembly imports
- `ConFigTree` typed variable on the root sequence
- `out_ConFigTree` OutArgument binding on `InvokeWorkflowFile`
- Two identity assertions (`IsNot Nothing`, `GetType().Name = "CodedConfig"`)

Property-value assertions (`ConFigTree.Settings.X = expected`) depend on the
project's test fixture data and must be added manually after verifying the
generated typed class against `Data/Config_Test.xlsx`.

`patch-testcase` is idempotent — re-running it on an already-patched file
preserves manually-added assertions. If the project files are reset from the
template, all manual additions are lost (the template does not include them).

## Key CLI flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--output-xaml PATH` | — | Write ClipboardData XAML snippet to file |
| `--generate-tostring` | off | Add `ToString()` override to each class |
| `--generate-tojson` | off | Add `ToJson()` / `FromJson()` helpers |
| `--readonly` | off | Use `{ get; init; }` instead of `{ get; set; }` |
| `--uipath-var NAME` | `out_ConFigTree` | Variable name used in the XAML snippet |

## Gotchas

- If Studio shows *"Please import the UiPath.CodedWorkflows package"*, re-run the Generate phase — the dependency is missing from `project.json`.
- The project must be reloaded in Studio after Generate completes — `UiPath.CodedWorkflows` is a new dependency and Studio must restore it before it can compile.
- `[WARN]` on stderr means a sheet had an unrecognised header row; output is still generated best-effort.
