"""
cli — argparse top-level dispatcher for config-tree subcommands.

Subcommands:
  detect               Read project.json; print DOTNET/ASSEMBLY/CONFIG env vars
  generate             Config.xlsx → C# (stdout) or XAML file
  patch-project        Add UiPath.CodedWorkflows dependency to project.json
  patch-init-settings  Patch Framework/InitAllSettings.xaml
  patch-testcase       Patch Tests/TestCase_InitAllSettings.xaml
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="config-tree",
        description="UiPath REFramework Config.xlsx → typed C# + XAML patcher",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # detect
    sub.add_parser(
        "detect",
        help="Read project.json and print shell-sourceable env vars",
    )

    # generate
    gen = sub.add_parser(
        "generate",
        help="Generate C# class (stdout) or XAML file from Config.xlsx",
    )
    gen.add_argument("file", metavar="CONFIG", help="Path to Config.xlsx")
    gen.add_argument(
        "--dotnet-version",
        dest="dotnet_version",
        default="net6",
        choices=["net6", "net8"],
        help="Target .NET version (default: net6)",
    )
    gen.add_argument(
        "--namespace",
        default="Cpmf.Config",
        help="C# namespace (default: Cpmf.Config)",
    )
    gen.add_argument(
        "--root-class",
        dest="root_class",
        default="CodedConfig",
        help="Root aggregator class name (default: CodedConfig)",
    )
    gen.add_argument(
        "--sheets",
        default=None,
        help="Comma-separated sheet names to include (default: all)",
    )
    gen.add_argument(
        "--generate-tostring",
        dest="generate_tostring",
        action="store_true",
        help="Emit ToString() override in generated C#",
    )
    gen.add_argument(
        "--generate-loader",
        dest="generate_loader",
        action="store_true",
        default=True,
        help="Emit Load() factory method (default: true)",
    )
    gen.add_argument(
        "--generate-tojson",
        dest="generate_tojson",
        action="store_true",
        help="Emit ToJson() method",
    )
    gen.add_argument(
        "--generate-pristine",
        dest="generate_pristine",
        action="store_true",
        help="Emit pristine default values",
    )
    gen.add_argument(
        "--readonly",
        action="store_true",
        help="Emit readonly properties",
    )
    gen.add_argument(
        "--uipath-var",
        dest="uipath_var",
        default="out_ConFigTree",
        help="UiPath variable name for XAML output (default: out_ConFigTree)",
    )
    gen.add_argument(
        "--xml-docs",
        dest="xml_docs",
        action="store_true",
        help="Emit XML doc comments",
    )
    gen.add_argument(
        "--fmt",
        default="text",
        choices=["text", "json"],
        help="Diagnostic output format (default: text)",
    )
    gen.add_argument(
        "--output-cs",
        dest="output_cs",
        metavar="FILE",
        type=Path,
        default=None,
        help="Write C# to FILE instead of stdout",
    )
    gen.add_argument(
        "--output-xaml",
        dest="output_xaml",
        metavar="FILE",
        type=Path,
        default=None,
        help="Write XAML ClipboardData file",
    )

    # patch-project
    pp = sub.add_parser(
        "patch-project",
        help="Add a NuGet dependency to project.json if absent",
    )
    pp.add_argument(
        "--package",
        default="UiPath.CodedWorkflows",
        help="Package name (default: UiPath.CodedWorkflows)",
    )
    pp.add_argument(
        "--version",
        default="24.10.1",
        help="Package version (default: 24.10.1)",
    )

    # patch-init-settings
    pis = sub.add_parser(
        "patch-init-settings",
        help="Patch Framework/InitAllSettings.xaml for typed config",
    )
    pis.add_argument("--assembly", required=True, help="Assembly name, e.g. MyProject.Core")
    pis.add_argument(
        "--xaml",
        required=True,
        metavar="FILE",
        help="Path to generated LoadTypedConfig.xaml snippet file",
    )

    # patch-testcase
    ptc = sub.add_parser(
        "patch-testcase",
        help="Patch Tests/TestCase_InitAllSettings.xaml for typed config",
    )
    ptc.add_argument("--assembly", required=True, help="Assembly name, e.g. MyProject.Core")

    args = parser.parse_args()

    if args.command == "detect":
        from config_tree import detect
        detect.run()

    elif args.command == "generate":
        from config_tree import generate
        args.file = Path(args.file)
        generate.run(args)

    elif args.command == "patch-project":
        from config_tree import patch_project
        patch_project.run(args.package, args.version)

    elif args.command == "patch-init-settings":
        from config_tree import patch_init_settings
        patch_init_settings.run(args.assembly, Path(args.xaml))

    elif args.command == "patch-testcase":
        from config_tree import patch_testcase
        patch_testcase.run(args.assembly)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
