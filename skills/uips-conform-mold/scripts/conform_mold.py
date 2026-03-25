# /// script
# requires-python = ">=3.11"
# dependencies = ["openpyxl"]
# ///
"""
ConFormMold — UiPath REFramework Config.xlsx → typed C# classes and XAML loader.

Reads ./Data/Config.xlsx (or a supplied path), detects Standard and Asset sheet
schemas, and generates:
  - A typed C# file with one class per sheet plus an AppConfig aggregator
  - Optionally a XAML workflow that loads Config.xlsx into those typed classes

Usage:
  uv run conform_mold.py [FILE] [OPTIONS]

Examples:
  uv run conform_mold.py
  uv run conform_mold.py ./Data/Config.xlsx --output-cs AppConfig.cs
  uv run conform_mold.py ./Data/Config.xlsx --output-cs AppConfig.cs --output-xaml LoadTypedConfig.xaml
  uv run conform_mold.py ./Data/Config.xlsx --sheets Settings,Constants
  uv run conform_mold.py ./Data/Config.xlsx --format json

Exit codes: 0 = success (warnings possible), 1 = fatal input error.
"""

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import openpyxl

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FILE = Path("./Data/Config.xlsx")
DEFAULT_NAMESPACE = "Cpmf.Config"
DEFAULT_ROOT_CLASS = "AppConfig"
DEFAULT_DOTNET = "net6"

_HEADER_STANDARD = ["name", "value", "description"]
_HEADER_ASSET = ["name", "asset", "orchestratorassetfolder", "description"]

# C# types that require `using System;`
_SYSTEM_TYPES = {"DateOnly", "DateTime", "TimeOnly"}

# ---------------------------------------------------------------------------
# Intermediate representation
# ---------------------------------------------------------------------------


@dataclass
class PropertyDef:
    prop_name: str
    cs_type: str
    description: str | None
    asset_name: str | None = None
    folder: str | None = None


@dataclass
class SheetDef:
    sheet_name: str
    class_name: str
    schema: str  # "standard" or "asset"
    properties: list[PropertyDef] = field(default_factory=list)


@dataclass
class WorkbookIR:
    root_class: str
    namespace: str
    dotnet_version: str
    emit_xml_docs: bool
    sheets: list[SheetDef] = field(default_factory=list)
    needs_orchestrator_asset: bool = False
    needs_system_using: bool = False


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def load_workbook(path: Path) -> openpyxl.Workbook:
    if path.suffix.lower() != ".xlsx":
        print(f"Error: expected a .xlsx file, got: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return openpyxl.load_workbook(path, data_only=True)
    except Exception as exc:
        print(f"Error: cannot open {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def detect_schema(header_row: list) -> str | None:
    """Return 'standard', 'asset', or None based on normalised header columns."""
    normalised = [str(v).strip().lower() if v is not None else "" for v in header_row]
    if len(normalised) >= 3 and normalised[:3] == _HEADER_STANDARD[:3]:
        return "standard"
    if len(normalised) >= 4 and normalised[:4] == _HEADER_ASSET:
        return "asset"
    return None


def read_sheet(ws) -> tuple[str, list[dict]]:
    """Return (schema, rows). Emits warnings and returns ('skip', []) for bad sheets."""
    all_rows = list(ws.iter_rows(values_only=True))
    if not all_rows or all(v is None for v in all_rows[0]):
        print(f"  [WARN] Sheet '{ws.title}': no header row found, skipping.", file=sys.stderr)
        return "skip", []

    header = list(all_rows[0])
    schema = detect_schema(header)
    if schema is None:
        print(
            f"  [WARN] Sheet '{ws.title}': unrecognised header {header[:4]}, skipping.",
            file=sys.stderr,
        )
        return "skip", []

    rows = []
    for raw in all_rows[1:]:
        if not raw or raw[0] is None or str(raw[0]).strip() == "":
            continue
        if schema == "standard":
            name = str(raw[0]).strip()
            value = raw[1] if len(raw) > 1 else None
            desc = str(raw[2]).strip() if len(raw) > 2 and raw[2] is not None else None
            rows.append({"name": name, "value": value, "description": desc})
        else:  # asset
            name = str(raw[0]).strip()
            asset_name = str(raw[1]).strip() if len(raw) > 1 and raw[1] is not None else ""
            folder = str(raw[2]).strip() if len(raw) > 2 and raw[2] is not None else ""
            desc = str(raw[3]).strip() if len(raw) > 3 and raw[3] is not None else None
            rows.append({"name": name, "asset_name": asset_name, "folder": folder, "description": desc})

    return schema, rows


def infer_cs_type(py_value, dotnet_version: str) -> str:
    """Map a Python value (from openpyxl data_only) to a C# type name."""
    if py_value is None:
        return "string"
    # bool must precede int — bool is a subclass of int in Python
    if isinstance(py_value, bool):
        return "bool"
    if isinstance(py_value, int):
        return "int"
    if isinstance(py_value, float):
        return "double"
    # datetime.time before datetime.datetime
    if isinstance(py_value, datetime.time) and not isinstance(py_value, datetime.datetime):
        return "TimeOnly"
    if isinstance(py_value, datetime.datetime):
        if py_value.hour == 0 and py_value.minute == 0 and py_value.second == 0 and py_value.microsecond == 0:
            return "DateOnly"
        return "DateTime"
    if isinstance(py_value, datetime.date):
        return "DateOnly"
    return "string"


def to_pascal_case(name: str) -> str:
    """Convert a config key name to PascalCase."""
    segments = re.split(r"[^a-zA-Z0-9]+", name)
    result = "".join(seg[0].upper() + seg[1:] for seg in segments if seg)
    if result and result[0].isdigit():
        result = "_" + result
    return result


def sheet_name_to_class_name(sheet_name: str) -> str:
    """Convert sheet name to C# class name: split on . and -, PascalCase, append Config."""
    segments = re.split(r"[.\-]", sheet_name)
    result = "".join(seg[0].upper() + seg[1:] for seg in segments if seg)
    return result + "Config"


# ---------------------------------------------------------------------------
# Build IR
# ---------------------------------------------------------------------------


def build_ir(
    wb: openpyxl.Workbook,
    sheet_filter: list[str] | None,
    namespace: str,
    root_class: str,
    dotnet_version: str,
    emit_xml_docs: bool,
) -> WorkbookIR:
    ir = WorkbookIR(
        root_class=root_class,
        namespace=namespace,
        dotnet_version=dotnet_version,
        emit_xml_docs=emit_xml_docs,
    )

    requested = set(sheet_filter) if sheet_filter else None
    if requested:
        for name in requested:
            if name not in wb.sheetnames:
                print(f"  [WARN] Requested sheet '{name}' not found in workbook.", file=sys.stderr)

    for ws in wb.worksheets:
        if requested and ws.title not in requested:
            continue

        schema, rows = read_sheet(ws)
        if schema == "skip":
            continue

        class_name = sheet_name_to_class_name(ws.title)
        sheet_def = SheetDef(sheet_name=ws.title, class_name=class_name, schema=schema)

        for row in rows:
            prop_name = to_pascal_case(row["name"])
            if schema == "standard":
                cs_type = infer_cs_type(row["value"], dotnet_version)
                sheet_def.properties.append(
                    PropertyDef(prop_name=prop_name, cs_type=cs_type, description=row["description"])
                )
                if cs_type in _SYSTEM_TYPES:
                    ir.needs_system_using = True
            else:  # asset
                sheet_def.properties.append(
                    PropertyDef(
                        prop_name=prop_name,
                        cs_type="OrchestratorAsset",
                        description=row["description"],
                        asset_name=row["asset_name"],
                        folder=row["folder"],
                    )
                )

        if schema == "asset":
            ir.needs_orchestrator_asset = True

        ir.sheets.append(sheet_def)

    return ir


# ---------------------------------------------------------------------------
# C# generation
# ---------------------------------------------------------------------------


def _xml_doc(description: str | None, emit: bool, indent: str) -> str:
    if not emit or not description:
        return ""
    safe = description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"{indent}/// <summary>{safe}</summary>\n"


def _property_initializer(cs_type: str) -> str:
    if cs_type == "string":
        return ' = "";'
    if cs_type == "OrchestratorAsset":
        return " = new();"
    return ""


def render_cs_orchestrator_asset_class() -> str:
    return """\
    public class OrchestratorAsset
    {
        public string AssetName { get; set; } = "";
        public string Folder { get; set; } = "";
    }"""


def render_cs_sheet_class(sheet: SheetDef, ir: WorkbookIR) -> str:
    lines = [f"    public class {sheet.class_name}", "    {"]
    for prop in sheet.properties:
        doc = _xml_doc(prop.description, ir.emit_xml_docs, "        ")
        if doc:
            lines.append(doc.rstrip("\n"))
        init = _property_initializer(prop.cs_type)
        lines.append(f"        public {prop.cs_type} {prop.prop_name} {{ get; set; }}{init}")
    lines.append("    }")
    return "\n".join(lines)


def render_cs_root_class(ir: WorkbookIR) -> str:
    lines = []
    if ir.emit_xml_docs:
        lines.append(f"    /// <summary>Root configuration object.</summary>")
    lines.append(f"    public class {ir.root_class}")
    lines.append("    {")
    for sheet in ir.sheets:
        lines.append(f"        public {sheet.class_name} {sheet.class_name[:-6]} {{ get; set; }} = new();")
    lines.append("    }")
    return "\n".join(lines)


def render_cs(ir: WorkbookIR) -> str:
    sections = []

    if ir.needs_system_using:
        sections.append("using System;\n")

    sections.append(f"namespace {ir.namespace}")
    sections.append("{")

    sections.append(render_cs_root_class(ir))
    sections.append("")

    if ir.needs_orchestrator_asset:
        sections.append(render_cs_orchestrator_asset_class())
        sections.append("")

    for sheet in ir.sheets:
        sections.append(render_cs_sheet_class(sheet, ir))
        sections.append("")

    # Remove trailing empty line inside namespace block
    if sections and sections[-1] == "":
        sections.pop()

    sections.append("}")
    return "\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# XAML generation
# ---------------------------------------------------------------------------

_VB_CONVERT = {
    "int": "CInt({val}.ToString())",
    "double": "CDbl({val}.ToString())",
    "bool": "CBool({val}.ToString())",
    "DateOnly": "DateOnly.Parse({val}.ToString())",
    "DateTime": "DateTime.Parse({val}.ToString())",
    "TimeOnly": "TimeOnly.Parse({val}.ToString())",
}


def _vb_assign_value(cs_type: str, col: str = 'row("Value")') -> str:
    if cs_type == "string":
        return f'{col}.ToString()'
    template = _VB_CONVERT.get(cs_type)
    if template:
        return template.replace("{val}", col)
    return f'{col}.ToString()'


def render_xaml_sheet_loader(sheet: SheetDef, ir: WorkbookIR) -> str:
    var = f"dt_{sheet.sheet_name.replace('.', '_').replace('-', '_')}"
    config_prop = f"config.{sheet.class_name[:-6]}"
    lines = []
    lines.append(f'    <!-- {sheet.sheet_name} -->')
    lines.append(f'    <ui:ForEachRow DisplayName="Map {sheet.sheet_name}" DataTable="[{var}]">')
    lines.append(f'      <ui:ForEachRow.Body>')
    lines.append(f'        <ActivityAction x:TypeArguments="sd:DataRow">')
    lines.append(f'          <ActivityAction.Argument>')
    lines.append(f'            <DelegateInArgument x:TypeArguments="sd:DataRow" Name="row" />')
    lines.append(f'          </ActivityAction.Argument>')
    lines.append(f'          <Switch x:TypeArguments="x:String" Expression="[row(&quot;Name&quot;).ToString()]">')

    for prop in sheet.properties:
        original_name = prop.prop_name  # PascalCase
        if sheet.schema == "standard":
            val_expr = _vb_assign_value(prop.cs_type)
            lines.append(f'            <Case Value="{original_name}">')
            lines.append(f'              <Assign><Assign.To><OutArgument x:TypeArguments="{_xaml_type(prop.cs_type)}"><VisualBasicReference x:TypeArguments="{_xaml_type(prop.cs_type)}">{config_prop}.{prop.prop_name}</VisualBasicReference></OutArgument></Assign.To><Assign.Value><InArgument x:TypeArguments="{_xaml_type(prop.cs_type)}">[{val_expr}]</InArgument></Assign.Value></Assign>')
            lines.append(f'            </Case>')
        else:  # asset
            lines.append(f'            <Case Value="{original_name}">')
            lines.append(f'              <Sequence>')
            lines.append(f'                <Assign><Assign.To><OutArgument x:TypeArguments="x:String"><VisualBasicReference x:TypeArguments="x:String">{config_prop}.{prop.prop_name}.AssetName</VisualBasicReference></OutArgument></Assign.To><Assign.Value><InArgument x:TypeArguments="x:String">[row("Asset").ToString()]</InArgument></Assign.Value></Assign>')
            lines.append(f'                <Assign><Assign.To><OutArgument x:TypeArguments="x:String"><VisualBasicReference x:TypeArguments="x:String">{config_prop}.{prop.prop_name}.Folder</VisualBasicReference></OutArgument></Assign.To><Assign.Value><InArgument x:TypeArguments="x:String">[row("OrchestratorAssetFolder").ToString()]</InArgument></Assign.Value></Assign>')
            lines.append(f'              </Sequence>')
            lines.append(f'            </Case>')

    lines.append(f'          </Switch>')
    lines.append(f'        </ActivityAction>')
    lines.append(f'      </ui:ForEachRow.Body>')
    lines.append(f'    </ui:ForEachRow>')
    return "\n".join(lines)


def _xaml_type(cs_type: str) -> str:
    mapping = {
        "string": "x:String",
        "int": "x:Int32",
        "double": "x:Double",
        "bool": "x:Boolean",
        "DateOnly": "x:DateTime",
        "DateTime": "x:DateTime",
        "TimeOnly": "x:TimeSpan",
        "OrchestratorAsset": "p:OrchestratorAsset",
    }
    return mapping.get(cs_type, "x:String")


def render_xaml(ir: WorkbookIR) -> str:
    ns_last = ir.namespace.split(".")[-1]
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Activity x:Class="LoadTypedConfig"')
    lines.append('  xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities"')
    lines.append('  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"')
    lines.append('  xmlns:ui="http://schemas.uipath.com/workflow/activities"')
    lines.append('  xmlns:sd="clr-namespace:System.Data;assembly=System.Data"')
    lines.append(f'  xmlns:p="clr-namespace:{ir.namespace};assembly={ns_last}">')
    lines.append('')
    lines.append('  <x:Members>')
    lines.append(f'    <x:Property Name="config" Type="p:{ir.root_class}" />')
    lines.append('  </x:Members>')
    lines.append('')
    lines.append('  <Sequence DisplayName="Load Config.xlsx">')
    lines.append('    <Sequence.Variables>')
    for sheet in ir.sheets:
        var = f"dt_{sheet.sheet_name.replace('.', '_').replace('-', '_')}"
        lines.append(f'      <Variable x:TypeArguments="sd:DataTable" Name="{var}" />')
    lines.append('    </Sequence.Variables>')
    lines.append('')
    lines.append('    <ui:ExcelApplicationScope WorkbookPath="Data\\Config.xlsx">')
    lines.append('      <ui:ExcelApplicationScope.Body>')
    lines.append('        <ActivityAction>')
    lines.append('          <ActivityAction.Argument>')
    lines.append('            <DelegateInArgument x:TypeArguments="ui:WorkbookApplication" Name="ExcelWorkbookScope" />')
    lines.append('          </ActivityAction.Argument>')
    lines.append('          <Sequence>')
    for sheet in ir.sheets:
        var = f"dt_{sheet.sheet_name.replace('.', '_').replace('-', '_')}"
        lines.append(f'            <ui:ReadRange SheetName="{sheet.sheet_name}" AddHeaders="True" DataTable="[{var}]" />')
    lines.append('          </Sequence>')
    lines.append('        </ActivityAction>')
    lines.append('      </ui:ExcelApplicationScope.Body>')
    lines.append('    </ui:ExcelApplicationScope>')
    lines.append('')
    for sheet in ir.sheets:
        lines.append(render_xaml_sheet_loader(sheet, ir))
    lines.append('')
    lines.append('  </Sequence>')
    lines.append('</Activity>')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def emit_diagnostics(ir: WorkbookIR, fmt: str, warnings: list[str]) -> None:
    if fmt == "json":
        data = {
            "sheets": [
                {"name": s.sheet_name, "class": s.class_name, "schema": s.schema, "properties": len(s.properties)}
                for s in ir.sheets
            ],
            "needs_orchestrator_asset": ir.needs_orchestrator_asset,
            "needs_system_using": ir.needs_system_using,
            "warnings": warnings,
        }
        print(json.dumps(data, indent=2), file=sys.stderr)
    else:
        print(
            f"ConFormMold: {len(ir.sheets)} sheet(s) processed"
            + (f", {len(warnings)} warning(s)" if warnings else ""),
            file=sys.stderr,
        )
        for s in ir.sheets:
            print(f"  {s.class_name} ({s.schema}, {len(s.properties)} properties)", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate typed C# config classes and XAML loader from UiPath Config.xlsx."
    )
    parser.add_argument(
        "file", nargs="?", type=Path, default=None,
        metavar="FILE",
        help=f"Path to Config.xlsx (default: {DEFAULT_FILE})",
    )
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE, help="C# namespace (default: Cpmf.Config)")
    parser.add_argument("--root-class", default=DEFAULT_ROOT_CLASS, dest="root_class", help="Root class name (default: AppConfig)")
    parser.add_argument("--dotnet-version", default=DEFAULT_DOTNET, choices=["net6", "net8"], dest="dotnet_version")
    parser.add_argument("--no-xml-docs", action="store_false", dest="xml_docs", default=True, help="Suppress XML doc comments")
    parser.add_argument("--sheets", default=None, help="Comma-separated sheet names to include")
    parser.add_argument("--output-cs", type=Path, default=None, dest="output_cs", help="Write C# to file (default: stdout)")
    parser.add_argument("--output-xaml", type=Path, default=None, dest="output_xaml", help="Write XAML to file")
    parser.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    args = parser.parse_args()

    path = args.file if args.file is not None else DEFAULT_FILE
    sheet_filter = [s.strip() for s in args.sheets.split(",")] if args.sheets else None

    wb = load_workbook(path)
    ir = build_ir(wb, sheet_filter, args.namespace, args.root_class, args.dotnet_version, args.xml_docs)

    cs_output = render_cs(ir)

    if args.output_cs:
        try:
            args.output_cs.write_text(cs_output, encoding="utf-8")
        except OSError as exc:
            print(f"Error: cannot write {args.output_cs}: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(cs_output, end="")

    if args.output_xaml:
        xaml_output = render_xaml(ir)
        try:
            args.output_xaml.write_text(xaml_output, encoding="utf-8")
        except OSError as exc:
            print(f"Error: cannot write {args.output_xaml}: {exc}", file=sys.stderr)
            sys.exit(1)

    emit_diagnostics(ir, args.fmt, [])


if __name__ == "__main__":
    main()
