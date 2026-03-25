"""
patch_init_settings — patch Framework/InitAllSettings.xaml for typed config.

Changes applied (all idempotent):
  - Add Cpmf.Config to TextExpression.NamespacesForImplementation
  - Add ASSEMBLY to TextExpression.ReferencesForImplementation
  - Add xmlns:cc on root Activity element
  - Add out_ConFigTree typed x:Property in x:Members
  - Remove x:Object local variable for out_ConFigTree
  - Promote OutArgument + InArgument types x:Object → cc:CodedConfig
  - Insert LoadTypedConfig.xaml ClipboardData.Data content at end of
    the "Initialize All Settings" Sequence (before </Sequence></Activity>)
"""

import re
import sys
from pathlib import Path


def run(assembly: str, xaml_snippet: Path) -> None:
    target = Path("Framework/InitAllSettings.xaml")
    if not target.exists():
        print("ERROR: Framework/InitAllSettings.xaml not found.", file=sys.stderr)
        sys.exit(1)
    if not xaml_snippet.exists():
        print(f"ERROR: {xaml_snippet} not found.", file=sys.stderr)
        sys.exit(1)

    original = target.read_text(encoding="utf-8")
    text = original

    # namespace import — insert inside sco:Collection, before its closing tag
    if "<x:String>Cpmf.Config</x:String>" not in text:
        text = re.sub(
            r"(\s*</sco:Collection>\s*</[^>]*NamespacesForImplementation>)",
            r"\n      <x:String>Cpmf.Config</x:String>\1",
            text, count=1,
        )

    # assembly reference (ReferencesForImplementation uses scg:List in InitAllSettings)
    asm_tag = f"<AssemblyReference>{assembly}</AssemblyReference>"
    if asm_tag not in text:
        text = re.sub(
            r"(\s*</scg:List>\s*</[^>]*ReferencesForImplementation>)",
            "\n      " + asm_tag + r"\1",
            text, count=1,
        )

    # xmlns:cc on root element (insert after xmlns:x)
    cc_xmlns = f'xmlns:cc="clr-namespace:Cpmf.Config;assembly={assembly}"'
    if cc_xmlns not in text:
        text = text.replace(
            'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"',
            'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n    ' + cc_xmlns,
            1,
        )

    # typed x:Property in x:Members
    if 'out_ConFigTree" Type="OutArgument(cc:CodedConfig)"' not in text:
        text = re.sub(
            r"(\s*</x:Members>)",
            r'\n    <x:Property Name="out_ConFigTree" Type="OutArgument(cc:CodedConfig)" />\1',
            text, count=1,
        )

    # remove x:Object local variable for out_ConFigTree
    text = re.sub(
        r'[ \t]*<Variable x:TypeArguments="x:Object" Name="out_ConFigTree" />\r?\n',
        "",
        text,
    )

    # promote argument types x:Object → cc:CodedConfig
    text = text.replace(
        'x:TypeArguments="x:Object">[out_ConFigTree]',
        'x:TypeArguments="cc:CodedConfig">[out_ConFigTree]',
    )
    text = text.replace(
        'x:TypeArguments="x:Object">[CodedConfig.Load(dt_Tables)]',
        'x:TypeArguments="cc:CodedConfig">[CodedConfig.Load(dt_Tables)]',
    )

    # insert clipboard snippet content at end of "Initialize All Settings" Sequence
    if "dt_Tables" not in text:
        clip = xaml_snippet.read_text(encoding="utf-8")
        m = re.search(r"<ClipboardData\.Data>(.*?)</ClipboardData\.Data>", clip, re.DOTALL)
        if not m:
            print(f"ERROR: {xaml_snippet} has no ClipboardData.Data element.", file=sys.stderr)
            sys.exit(1)
        # ClipboardData.Data wraps its content in <scg:List x:TypeArguments="x:Object">.
        # Unwrap to get just the inner Activity element — Sequence only accepts Activity children.
        raw = m.group(1).strip()
        inner = re.search(r"<scg:List[^>]*>(.*?)</scg:List>", raw, re.DOTALL)
        paste = inner.group(1).strip() if inner else raw
        # The clipboard fragment uses xmlns:p for the default activity namespace.
        # In the parent document the default namespace covers these — strip the prefix.
        paste = paste.replace("<p:", "<").replace("</p:", "</")
        # The snippet declares out_ConFigTree as a local x:Object variable, which
        # would shadow the outer OutArgument(cc:CodedConfig) — remove it so the
        # Assign writes directly to the workflow argument.
        paste = re.sub(
            r'<Variable x:TypeArguments="x:Object" Name="out_ConFigTree" />\s*',
            "",
            paste,
        )
        # Promote the OutArgument and InArgument types in the snippet to cc:CodedConfig.
        paste = paste.replace(
            'x:TypeArguments="x:Object">[out_ConFigTree]',
            f'x:TypeArguments="cc:CodedConfig">[out_ConFigTree]',
        )
        paste = paste.replace(
            'x:TypeArguments="x:Object">[CodedConfig.Load(dt_Tables)]',
            f'x:TypeArguments="cc:CodedConfig">[CodedConfig.Load(dt_Tables)]',
        )
        marker = "\n  </Sequence>\n</Activity>"
        idx = text.rfind(marker)
        if idx == -1:
            print("ERROR: cannot find </Sequence></Activity> insertion point.", file=sys.stderr)
            sys.exit(1)
        text = text[:idx] + "\n    " + paste + text[idx:]

    if text != original:
        target.write_text(text, encoding="utf-8")
        print("Framework/InitAllSettings.xaml patched")
    else:
        print("Framework/InitAllSettings.xaml already up to date")
