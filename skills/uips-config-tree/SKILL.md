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
  version: "0.1.0"
allowed-tools: Bash
---

# UiPath REFramework — Typed Config Class Generator

Automates tasks 1 and 4 of the integration workflow. Tasks 2–10 require
manual action in UiPath Studio and must be handed off to the user.

## Entry guard

Before proceeding, verify the working directory is a REFramework project.
Two files must exist:

```bash
# Both must be present — abort if either is missing
test -f Framework/InitAllSettings.xaml
ls Data/Config*.xlsx
```

| Check | Path | Absence means |
|---|---|---|
| REFramework indicator | `Framework/InitAllSettings.xaml` | Not a REFramework project — skill does not apply |
| Config input | `Data/Config*.xlsx` | Nothing to generate from — ask user for the file location |

If either check fails, stop and tell the user this skill targets REFramework
template-based projects and cannot proceed without these files.

## Version detection

Read `project.json` and extract the `UiPath.System.Activities` dependency
version to determine the REFramework template generation and the correct
`--dotnet-version` flag:

```bash
python -c "
import json, re
data = json.load(open('project.json'))
sys_act = data.get('dependencies', {}).get('UiPath.System.Activities', '[22')
major = int(re.search(r'\[(\d+)', sys_act).group(1))
print('net8' if major >= 25 else 'net6')
"
```

| `UiPath.System.Activities` | REF template | `--dotnet-version` |
|---|---|---|
| `[25.*]` | v25.0.0 | `net8` |
| `[22.*]` / `[23.*]` / `[24.*]` | v23.10.0 or v24.10.0 | `net6` (default) |

v23 and v24 share identical dependency versions and cannot be distinguished
from `project.json` alone — treat both as `net6`.

Also read the project `name` from `project.json` — the assembly name used in
all Studio integration steps is `{name}.Core`:

```bash
ASSEMBLY=$(python -c "import json; print(json.load(open('project.json'))['name'] + '.Core')")
```

## Automated tasks (agent executes)

Resolve both variables first, then run the generator once for both outputs:

```bash
DOTNET=$(python -c "
import json, re
data = json.load(open('project.json'))
sys_act = data.get('dependencies', {}).get('UiPath.System.Activities', '[22')
major = int(re.search(r'\[(\d+)', sys_act).group(1))
print('net8' if major >= 25 else 'net6')
")
ASSEMBLY=$(python -c "import json; print(json.load(open('project.json'))['name'] + '.Core')")
CONFIG=$(ls Data/Config*.xlsx | head -1)

# Task 1 — C# to stdout, save to Lib/Config.cs
uv run skills/uips-conform-mold/scripts/conform_mold.py "$CONFIG" \
    --generate-tostring \
    --dotnet-version "$DOTNET" \
    > Lib/Config.cs

# Task 4 — XAML clipboard snippet to file
uv run skills/uips-conform-mold/scripts/conform_mold.py "$CONFIG" \
    --generate-tostring \
    --dotnet-version "$DOTNET" \
    --output-xaml LoadTypedConfig.xaml
```

`Lib/Config.cs` is ready to copy into the project.
`LoadTypedConfig.xaml` is written as UTF-8 (no BOM). User must open in
Notepad, Ctrl+A, Ctrl+C before pasting into Studio — do not copy from
terminal or chat output.

## Manual tasks (hand off to user)

After running the script, instruct the user to perform these steps in order
in UiPath Studio.

---

### Task 2 — Copy Config.cs into the project

Copy the generated file to:

```
Lib/Config.cs
```

---

### Task 3 — Open project in Studio

Open the project. Studio detects `Lib/Config.cs` and automatically adds
`UiPath.CodedWorkflows` to `project.json`:

```diff
+    "UiPath.CodedWorkflows": "[24.10.2]",
```

---

### Task 5 — Paste XAML snippet into InitAllSettings.xaml

Open `Framework/InitAllSettings.xaml`. Click at the bottom of the
**"Initialize All Settings"** Sequence (after the existing settings-loading
block). Paste from the file (Notepad → Ctrl+A → Ctrl+C → Studio Ctrl+V).

Studio automatically adds these namespace imports on paste:

```diff
+      <x:String>System.ComponentModel</x:String>
+      <x:String>UiPath.Excel</x:String>
+      <x:String>UiPath.Excel.Activities</x:String>
+      <AssemblyReference>System.ComponentModel.EventBasedAsync</AssemblyReference>
+      <AssemblyReference>UiPath.Excel.Activities.Design</AssemblyReference>
```

All other `±` lines in the diff are `sap:VirtualizedContainerService.HintSize`
layout noise — no logic change.

---

### Task 6 — Import namespace Cpmf.Config

Open the Imports panel in Studio (or right-click → Import Namespaces).
Add `Cpmf.Config`. Studio resolves the assembly name from the project name.

```diff
+      <x:String>Cpmf.Config</x:String>
+      <AssemblyReference>{ASSEMBLY}</AssemblyReference>
```

`{ASSEMBLY}` = `project.json → name` + `.Core` (e.g. `MyProject.Core`).
Studio resolves the assembly name from the project name automatically.

---

### Task 7 — Promote out_ConFigTree to typed OutArgument

Three edits in `Framework/InitAllSettings.xaml`:

**7a.** Add `xmlns:cc` to the root Activity element:

```diff
+xmlns:cc="clr-namespace:Cpmf.Config;assembly={ASSEMBLY}"
```

**7b.** Declare `out_ConFigTree` as a typed OutArgument in `x:Members`:

```diff
+<x:Property Name="out_ConFigTree" Type="OutArgument(cc:CodedConfig)" />
```

**7c.** Remove the local variable and change both argument types from
`x:Object` to `cc:CodedConfig`:

```diff
-<Variable x:TypeArguments="x:Object" Name="out_ConFigTree" />

-<OutArgument x:TypeArguments="x:Object">[out_ConFigTree]</OutArgument>
+<OutArgument x:TypeArguments="cc:CodedConfig">[out_ConFigTree]</OutArgument>

-<InArgument x:TypeArguments="x:Object">[CodedConfig.Load(dt_Tables)]</InArgument>
+<InArgument x:TypeArguments="cc:CodedConfig">[CodedConfig.Load(dt_Tables)]</InArgument>
```

---

### Task 8 — Declare typed receiver variable in TestCase

In `Tests/TestCase_InitAllSettings.xaml`, add `xmlns:cc` to the root element:

```diff
+xmlns:cc="clr-namespace:Cpmf.Config;assembly={ASSEMBLY}"
```

Add `ConFigTree` as a variable at the **parent** TestCase sequence (not inside
`... When` or `... Then`) so it is in scope for all child sequences:

```xml
<Variable x:TypeArguments="cc:CodedConfig" Name="ConFigTree" />
```

---

### Task 9 — Add OutArgument binding to InvokeWorkflowFile

In `Tests/TestCase_InitAllSettings.xaml`, add the following entry inside
`InvokeWorkflowFile.Arguments` for the `InitAllSettings` invocation:

```xml
<OutArgument x:TypeArguments="cc:CodedConfig" x:Key="out_ConFigTree">[ConFigTree]</OutArgument>
```

---

### Task 10 — Add ConFigTree assertions to the Then sequence

Append to the `... Then` sequence in `Tests/TestCase_InitAllSettings.xaml`:

**Object identity checks:**

```xml
<uta:VerifyExpression DisplayName="ConFigTree: object is not Nothing"
    Expression="[ConFigTree IsNot Nothing]"
    OutputMessageFormat="[&quot;actual: &quot; + (ConFigTree IsNot Nothing).ToString()]"
    ContinueOnFailure="True" />
<uta:VerifyExpression DisplayName="ConFigTree: type is CodedConfig"
    Expression="[ConFigTree.GetType().Name = &quot;CodedConfig&quot;]"
    OutputMessageFormat="[&quot;actual: &quot; + ConFigTree.GetType().Name]"
    ContinueOnFailure="True" />
```

**Typed property assertions (new `... Then (ConFigTree typed properties)` sequence):**

| Expression | Expected |
|---|---|
| `ConFigTree.Settings.FeatureName = "TypesDemo"` | string match |
| `ConFigTree.Settings.MaxItems = 42` | int match |
| `ConFigTree.Settings.IsEnabled = True` | bool match |
| `ConFigTree.Constants.MaxRetryNumber = 0` | int match |
| `ConFigTree.Constants.StrictMode = False` | bool match |

All use `ContinueOnFailure="True"`.

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
