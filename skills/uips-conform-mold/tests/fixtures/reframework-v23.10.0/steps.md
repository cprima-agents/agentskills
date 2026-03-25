# Manual integration steps — REFramework v23.10.0

Source: https://github.com/rpapub/ConFormMold/issues/43

These are the ordered manual edits applied to the REFramework project after running
`conform_mold.py`. Each step corresponds to a distinct Studio save / git diff.

---

## Step 1 — Place Config.cs

Copy the generated `Config.cs` into the project:

```
Lib/Config.cs
```

Open the project in UiPath Studio. Studio auto-adds `UiPath.CodedWorkflows` to
`project.json` (required for coded workflow / typed class access).

---

## Step 2 — Paste ClipboardData snippet into InitAllSettings.xaml

Open `Framework/InitAllSettings.xaml` in UiPath Studio.

Paste the `expected.xaml` clipboard content **at the bottom of the
"Initialize All Settings" Sequence** (after the existing settings-loading block).

Studio auto-adds namespace imports on paste:
- `System.ComponentModel`, `UiPath.Excel`, `UiPath.Excel.Activities`
- Assembly references: `System.ComponentModel.EventBasedAsync`, `UiPath.Excel.Activities.Design`

All other `±` lines in the diff are `sap:VirtualizedContainerService.HintSize` layout noise.

The pasted sequence structure:

```xml
<Sequence DisplayName="out_ConFigTree" ...>
  <Sequence.Variables>
    <Variable x:TypeArguments="scg:Dictionary(x:String, sd:DataTable)" Name="dt_Tables" />
    <Variable x:TypeArguments="x:Object" Name="out_ConFigTree" />   <!-- x:Object at this stage -->
  </Sequence.Variables>
  <Assign DisplayName="Initialize dt_Tables">
    dt_Tables = New Dictionary(Of String, DataTable)
  </Assign>
  <ui:ForEach DisplayName="For each sheet — ReadRange into dt_Tables" Values="[in_ConfigSheets]">
    <Sequence DisplayName="Read sheet into dt_Tables">
      <ui:ReadRange SheetName="[Sheet]" WorkbookPath="[in_ConfigFile]" DataTable="[dt_CurrentSheet]" />
      <Assign DisplayName="Add sheet to dt_Tables">dt_Tables(Sheet) = dt_CurrentSheet</Assign>
    </Sequence>
  </ui:ForEach>
  <Assign DisplayName="Load ConFigTree">
    out_ConFigTree = CodedConfig.Load(dt_Tables)
  </Assign>
</Sequence>
```

---

## Step 3 — Import namespace Cpmf.Config

In Studio, import the `Cpmf.Config` namespace (Imports panel or right-click → Import Namespaces).

Diff in `InitAllSettings.xaml`:

```diff
+      <x:String>Cpmf.Config</x:String>
+      <AssemblyReference>ConFormMold_REF_v23.Core</AssemblyReference>
```

`ConFormMold_REF_v23.Core` is the compiled assembly name — Studio resolves it from the project name. `CodedConfig.Load(dt_Tables)` can now resolve to the typed class.

---

## Step 4 — Promote out_ConFigTree to OutArgument(cc:CodedConfig)

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

Studio also auto-adds serialization + Linq.Expressions assembly references (noise).

---

## Step 5 — Wire out_ConFigTree in TestCase_InitAllSettings.xaml

In `Tests/TestCase_InitAllSettings.xaml`:

**5a. Add `xmlns:cc` to root:**

```diff
+xmlns:cc="clr-namespace:Cpmf.Config;assembly=ConFormMold_REF_v23.Core"
```

**5b. Declare typed receiver variable at top-level TestCase sequence:**

```xml
<Variable x:TypeArguments="cc:CodedConfig" Name="ConFigTree" />
```

Scoped at the parent sequence so it is in scope for both `... When` and all `... Then` sequences.

**5c. Wire into InvokeWorkflowFile.Arguments:**

```xml
<OutArgument x:TypeArguments="cc:CodedConfig" x:Key="out_ConFigTree">[ConFigTree]</OutArgument>
```

---

## Step 6 — Add ConFigTree assertions to TestCase

Append to the `... Then` sequence in `Tests/TestCase_InitAllSettings.xaml`:

**Object identity checks (VerifyExpression_7–8):**

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

**Typed property assertions — new `... Then (ConFigTree typed properties)` sequence (VerifyExpression_9–13):**

| Expression | Expected |
|---|---|
| `ConFigTree.Settings.FeatureName = "TypesDemo"` | string match |
| `ConFigTree.Settings.MaxItems = 42` | int match |
| `ConFigTree.Settings.IsEnabled = True` | bool match |
| `ConFigTree.Constants.MaxRetryNumber = 0` | int match |
| `ConFigTree.Constants.StrictMode = False` | bool match |

All use `ContinueOnFailure="True"`.
