---
name: uips-conform-mold
description: >
  Generate typed C# config classes and a UiPath clipboard snippet from a
  UiPath REFramework Config.xlsx. Use when a developer asks to set up typed
  config access in a REFramework project; when they want to replace
  dictionary-based settings lookups with strongly-typed C# properties; when
  they need a CodedConfig class with per-sheet FromDataTable loaders and a
  root Load() factory. Triggers on: typed config, CodedConfig, ConFormMold,
  Config.xlsx, InitAllSettings, typed settings, REFramework config class.
license: Apache-2.0
compatibility: Requires Python 3.11+ and uv. Input must be a UiPath Config.xlsx with Name/Value column headers per sheet.
metadata:
  author: cprima
  version: "0.1.0"
allowed-tools: Bash
---

# UiPath REFramework — Typed Config Class Generator

Generate a typed C# `CodedConfig` class and a UiPath clipboard snippet from
a REFramework `Config.xlsx`. Paste the snippet into `InitAllSettings.xaml` to
wire typed config loading into the framework.

## Run the script

```bash
# C# to stdout + XAML to file
uv run skills/uips-conform-mold/scripts/conform_mold.py Data/Config.xlsx \
    --generate-tostring \
    --output-xaml LoadTypedConfig.xaml

# C# only (no XAML)
uv run skills/uips-conform-mold/scripts/conform_mold.py Data/Config.xlsx

# Read-only properties ({ get; init; })
uv run skills/uips-conform-mold/scripts/conform_mold.py Data/Config.xlsx --readonly
```

## Key CLI flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--output-xaml PATH` | — | Write ClipboardData XAML snippet to file |
| `--generate-tostring` | off | Add `ToString()` override to each class |
| `--generate-tojson` | off | Add `ToJson()` / `FromJson()` helpers |
| `--generate-pristine` | off | Emit a clean class with no extra methods |
| `--no-loader` | off | Suppress `FromDataTable` / `Load()` methods |
| `--readonly` | off | Use `{ get; init; }` instead of `{ get; set; }` |
| `--uipath-var NAME` | `out_ConFigTree` | Variable name used in the XAML snippet |

## Manual integration steps — REFramework v23.10.0

After running the script, apply these steps in UiPath Studio in order.
Each step corresponds to a distinct Studio save / git diff.

Source: <https://github.com/rpapub/ConFormMold/issues/43>

---

### Step 1 — Place Config.cs

Copy the generated C# output into the project:

```
Lib/Config.cs
```

Open the project in UiPath Studio. Studio auto-adds `UiPath.CodedWorkflows` to
`project.json` (required for coded workflow / typed class access).

---

### Step 2 — Paste ClipboardData snippet into InitAllSettings.xaml

Open `Framework/InitAllSettings.xaml` in UiPath Studio.

Open the generated XAML file in Notepad, Ctrl+A, Ctrl+C. Paste **at the bottom
of the "Initialize All Settings" Sequence** (after the existing settings-loading
block).

Studio auto-adds namespace imports on paste:
- `System.ComponentModel`, `UiPath.Excel`, `UiPath.Excel.Activities`
- Assembly references: `System.ComponentModel.EventBasedAsync`, `UiPath.Excel.Activities.Design`

The pasted sequence structure:

```xml
<Sequence DisplayName="out_ConFigTree">
  <Sequence.Variables>
    <Variable Name="dt_Tables" />          <!-- Dictionary(Of String, DataTable) -->
    <Variable Name="out_ConFigTree" />     <!-- x:Object at this stage -->
  </Sequence.Variables>
  <Assign DisplayName="Initialize dt_Tables" />
  <ui:ForEach DisplayName="For each sheet — ReadRange into dt_Tables">
    <Sequence DisplayName="Read sheet into dt_Tables">
      <ui:ReadRange WorkbookPath="[in_ConfigFile]" SheetName="[Sheet]" />
      <Assign DisplayName="Add sheet to dt_Tables" />
    </Sequence>
  </ui:ForEach>
  <Assign DisplayName="Load ConFigTree">
    out_ConFigTree = CodedConfig.Load(dt_Tables)
  </Assign>
</Sequence>
```

---

### Step 3 — Import namespace Cpmf.Config

In Studio, import the `Cpmf.Config` namespace (Imports panel or right-click →
Import Namespaces).

Diff in `InitAllSettings.xaml`:

```diff
+      <x:String>Cpmf.Config</x:String>
+      <AssemblyReference>ConFormMold_REF_v23.Core</AssemblyReference>
```

`ConFormMold_REF_v23.Core` is the compiled assembly name — Studio resolves it
from the project name. `CodedConfig.Load(dt_Tables)` can now resolve to the
typed class.

---

### Step 4 — Promote out_ConFigTree to OutArgument(cc:CodedConfig)

Three changes in `InitAllSettings.xaml`:

**4a. Add `xmlns:cc` to the root Activity element:**

```diff
+xmlns:cc="clr-namespace:Cpmf.Config;assembly=ConFormMold_REF_v23.Core"
```

**4b. Declare `out_ConFigTree` as a typed OutArgument in `x:Members`:**

```diff
+<x:Property Name="out_ConFigTree" Type="OutArgument(cc:CodedConfig)" />
```

**4c. Remove local variable; update Load Assign types:**

```diff
-<Variable x:TypeArguments="x:Object" Name="out_ConFigTree" />

-<OutArgument x:TypeArguments="x:Object">[out_ConFigTree]</OutArgument>
+<OutArgument x:TypeArguments="cc:CodedConfig">[out_ConFigTree]</OutArgument>

-<InArgument x:TypeArguments="x:Object">[CodedConfig.Load(dt_Tables)]</InArgument>
+<InArgument x:TypeArguments="cc:CodedConfig">[CodedConfig.Load(dt_Tables)]</InArgument>
```

---

### Step 5 — Wire out_ConFigTree in TestCase_InitAllSettings.xaml

In `Tests/TestCase_InitAllSettings.xaml`:

**5a. Add `xmlns:cc` to root:**

```diff
+xmlns:cc="clr-namespace:Cpmf.Config;assembly=ConFormMold_REF_v23.Core"
```

**5b. Declare typed receiver variable at top-level TestCase sequence:**

```xml
<Variable x:TypeArguments="cc:CodedConfig" Name="ConFigTree" />
```

Scoped at the parent sequence so it is in scope for both `... When` and all
`... Then` sequences.

**5c. Wire into InvokeWorkflowFile.Arguments:**

```xml
<OutArgument x:TypeArguments="cc:CodedConfig" x:Key="out_ConFigTree">[ConFigTree]</OutArgument>
```

---

### Step 6 — Add ConFigTree assertions to TestCase

Append to the `... Then` sequence in `Tests/TestCase_InitAllSettings.xaml`:

**Object identity checks:**

```xml
<uta:VerifyExpression DisplayName="ConFigTree: object is not Nothing"
    Expression="[ConFigTree IsNot Nothing]"
    ContinueOnFailure="True" />
<uta:VerifyExpression DisplayName="ConFigTree: type is CodedConfig"
    Expression="[ConFigTree.GetType().Name = &quot;CodedConfig&quot;]"
    ContinueOnFailure="True" />
```

**Typed property assertions:**

| Expression | Expected |
|---|---|
| `ConFigTree.Settings.FeatureName = "TypesDemo"` | string match |
| `ConFigTree.Settings.MaxItems = 42` | int match |
| `ConFigTree.Settings.IsEnabled = True` | bool match |
| `ConFigTree.Constants.MaxRetryNumber = 0` | int match |
| `ConFigTree.Constants.StrictMode = False` | bool match |

All use `ContinueOnFailure="True"`.

## Gotchas

- Paste from the **file** (open in Notepad, Ctrl+A, Ctrl+C) — do not copy from a terminal or chat output. Clipboard paste from text with a preceding BOM or whitespace will be rejected by Studio with an XML declaration error.
- The XML declaration in the generated file says `encoding="utf-16"` but the file is written as UTF-8. This is intentional — it matches the format produced by UiPath Studio itself.
- Steps 3–6 are manual Studio operations; there is no script automation for them.
- `[WARN]` on stderr indicates a sheet with an unrecognised header row. Output is still generated (best-effort).
