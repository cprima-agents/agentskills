"""
patch_testcase — patch Tests/TestCase_InitAllSettings.xaml for typed config.

Changes applied (all idempotent):
  - Add xmlns:cc on root Activity element
  - Add Cpmf.Config to TextExpression.NamespacesForImplementation
  - Add ASSEMBLY to TextExpression.ReferencesForImplementation
  - Add ConFigTree typed variable on root TestCase sequence
  - Add out_ConFigTree OutArgument binding on InvokeWorkflowFile
  - Add two identity VerifyExpression assertions to ... Then sequence
"""

import re
import sys
from pathlib import Path


_VERIFY_IDENTITY = (
    '\n      <uta:VerifyExpression'
    ' AlternativeVerificationTitle="{x:Null}" KeepScreenshots="{x:Null}"'
    ' OutputMessageFormat="[&quot;actual: &quot; + (ConFigTree IsNot Nothing).ToString()]"'
    ' Result="{x:Null}" ScreenshotsPath="{x:Null}" ContinueOnFailure="True"'
    ' DisplayName="ConFigTree: object is not Nothing"'
    ' Expression="[ConFigTree IsNot Nothing]"'
    ' sap:VirtualizedContainerService.HintSize="416,123"'
    ' TakeScreenshotInCaseOfFailingAssertion="False"'
    ' TakeScreenshotInCaseOfSucceedingAssertion="False" />'
    '\n      <uta:VerifyExpression'
    ' AlternativeVerificationTitle="{x:Null}" KeepScreenshots="{x:Null}"'
    ' OutputMessageFormat="[&quot;actual: &quot; + ConFigTree.GetType().Name]"'
    ' Result="{x:Null}" ScreenshotsPath="{x:Null}" ContinueOnFailure="True"'
    ' DisplayName="ConFigTree: type is CodedConfig"'
    ' Expression="[ConFigTree.GetType().Name = &quot;CodedConfig&quot;]"'
    ' sap:VirtualizedContainerService.HintSize="416,123"'
    ' TakeScreenshotInCaseOfFailingAssertion="False"'
    ' TakeScreenshotInCaseOfSucceedingAssertion="False" />'
)


def run(assembly: str) -> None:
    target = Path("Tests/TestCase_InitAllSettings.xaml")
    if not target.exists():
        print("ERROR: Tests/TestCase_InitAllSettings.xaml not found.", file=sys.stderr)
        sys.exit(1)

    original = target.read_text(encoding="utf-8")
    text = original

    # xmlns:cc on root element
    cc_xmlns = f'xmlns:cc="clr-namespace:Cpmf.Config;assembly={assembly}"'
    if cc_xmlns not in text:
        text = text.replace(
            'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"',
            'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n    ' + cc_xmlns,
            1,
        )

    # namespace import — insert inside sco:Collection, before its closing tag
    if "<x:String>Cpmf.Config</x:String>" not in text:
        text = re.sub(
            r"(\s*</sco:Collection>\s*</[^>]*NamespacesForImplementation>)",
            r"\n      <x:String>Cpmf.Config</x:String>\1",
            text, count=1,
        )

    # assembly reference (TestCase uses sco:Collection for references)
    asm_tag = f"<AssemblyReference>{assembly}</AssemblyReference>"
    if asm_tag not in text:
        text = re.sub(
            r"(\s*</sco:Collection>\s*</[^>]*ReferencesForImplementation>)",
            "\n      " + asm_tag + r"\1",
            text, count=1,
        )

    # ConFigTree variable on root TestCase sequence
    if 'Name="ConFigTree"' not in text:
        var_block = (
            '\n    <Sequence.Variables>'
            '\n      <Variable x:TypeArguments="cc:CodedConfig" Name="ConFigTree" />'
            '\n    </Sequence.Variables>'
        )
        text = text.replace(
            '\n    <Sequence DisplayName="... Given"',
            var_block + '\n    <Sequence DisplayName="... Given"',
            1,
        )

    # OutArgument binding on InvokeWorkflowFile
    if 'x:Key="out_ConFigTree"' not in text:
        text = text.replace(
            "</ui:InvokeWorkflowFile.Arguments>",
            '          <OutArgument x:TypeArguments="cc:CodedConfig"'
            ' x:Key="out_ConFigTree">[ConFigTree]</OutArgument>'
            "\n        </ui:InvokeWorkflowFile.Arguments>",
            1,
        )

    # Identity assertions appended to ... Then sequence
    if "ConFigTree IsNot Nothing" not in text:
        marker = "\n    </Sequence>\n  </Sequence>\n</Activity>"
        idx = text.rfind(marker)
        if idx == -1:
            print("ERROR: cannot find assertion insertion point.", file=sys.stderr)
            sys.exit(1)
        text = text[:idx] + _VERIFY_IDENTITY + text[idx:]

    if text != original:
        target.write_text(text, encoding="utf-8")
        print("Tests/TestCase_InitAllSettings.xaml patched")
    else:
        print("Tests/TestCase_InitAllSettings.xaml already up to date")
