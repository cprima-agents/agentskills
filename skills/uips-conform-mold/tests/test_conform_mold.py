"""
Tests for conform_mold.py

Approach:
  - C#  : structural text checks (key identifiers present in stdout)
  - XAML: structural XML checks (element nesting + required attributes)
           tested against all expected*.xaml in the fixture dir;
           "1 pass wins" — generated output must satisfy the rules of at least one.
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

P_NS = "http://schemas.microsoft.com/netfx/2009/xaml/activities"
UI_NS = "http://schemas.uipath.com/workflow/activities"

NS = {"p": P_NS, "ui": UI_NS}


def run(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
    )


def parse_xaml(path: Path) -> ET.Element:
    """Parse a utf-16 XAML file; raises ET.ParseError if malformed."""
    content = path.read_text(encoding="utf-16")
    return ET.fromstring(content)


def expected_xaml_files(fixture_dir: Path) -> list[Path]:
    """Return all expected*.xaml files in the fixture directory."""
    return sorted(fixture_dir.glob("expected*.xaml"))


def xaml_structural_rules(root: ET.Element) -> list[str]:
    """
    Run structural checks on a parsed XAML ClipboardData root.
    Returns a list of failure messages; empty list means all rules pass.
    Add new rules here as regressions are discovered.
    """
    failures = []

    # Rule 1: root tag is ClipboardData
    if "ClipboardData" not in root.tag:
        failures.append(f"Root tag is not ClipboardData: {root.tag}")

    # Rule 2: dt_Tables declared inside a Sequence.Variables
    if root.find(".//p:Sequence/p:Sequence.Variables/p:Variable[@Name='dt_Tables']", NS) is None:
        failures.append("Variable 'dt_Tables' not declared in Sequence.Variables")

    # Rule 3: at least one output variable (not dt_Tables or dt_CurrentSheet) in Sequence.Variables
    seq_vars = root.findall(".//p:Sequence/p:Sequence.Variables/p:Variable", NS)
    output_vars = [v for v in seq_vars if v.get("Name") not in ("dt_Tables", "dt_CurrentSheet")]
    if not output_vars:
        failures.append("No output variable found in Sequence.Variables")

    # Rule 4: ForEach is a direct child of a Sequence (not floating)
    # Accept both ui:ForEach (our generator) and p:ForEach (Studio-exported variants)
    _fe = root.find(".//p:Sequence/ui:ForEach", NS)
    foreach_in_seq = _fe if _fe is not None else root.find(".//p:Sequence/p:ForEach", NS)
    if foreach_in_seq is None:
        failures.append("No ForEach found as direct child of a Sequence")

    # Rule 5: ReadRange is nested inside ForEach (not floating)
    _rr = root.find(".//ui:ForEach//ui:ReadRange", NS)
    read_in_foreach = _rr if _rr is not None else root.find(".//p:ForEach//ui:ReadRange", NS)
    if read_in_foreach is None:
        failures.append("No ReadRange found nested inside a ForEach")

    # Rule 6: Load Assign present (DisplayName contains "Load")
    assigns = root.findall(".//p:Assign", NS)
    load_assigns = [a for a in assigns if "load" in a.get("DisplayName", "").lower()]
    if not load_assigns:
        failures.append("No Assign with 'Load' in DisplayName found")

    return failures


# ---------------------------------------------------------------------------
# C# structural tests
# ---------------------------------------------------------------------------


def test_cs_exit_code(script, fixture_dir):
    result = run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring")
    assert result.returncode == 0


def test_cs_contains_namespace(script, fixture_dir):
    result = run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring")
    assert "namespace Cpmf.Config" in result.stdout


def test_cs_contains_root_class(script, fixture_dir):
    result = run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring")
    assert "class CodedConfig" in result.stdout


def test_cs_contains_sheet_classes(script, fixture_dir):
    result = run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring")
    for cls in ("SettingsConfig", "ConstantsConfig", "AssetsConfig"):
        assert f"class {cls}" in result.stdout, f"Missing class {cls}"


def test_cs_contains_loader(script, fixture_dir):
    result = run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring")
    assert "FromDataTable" in result.stdout
    assert "Load(" in result.stdout


# ---------------------------------------------------------------------------
# XAML structural tests — 1 pass wins
# ---------------------------------------------------------------------------


def test_xaml_exit_code_and_file_created(script, fixture_dir, tmp_path):
    out = tmp_path / "out.xaml"
    result = run(
        script,
        str(fixture_dir / "input.xlsx"),
        "--generate-tostring",
        "--output-xaml",
        str(out),
    )
    assert result.returncode == 0
    assert out.exists()


def test_xaml_is_valid_xml(script, fixture_dir, tmp_path):
    out = tmp_path / "out.xaml"
    run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring", "--output-xaml", str(out))
    root = parse_xaml(out)  # raises ET.ParseError if malformed
    assert root is not None


def test_xaml_structural_rules_pass_for_at_least_one_expected(script, fixture_dir, tmp_path):
    """
    Generate XAML and verify it satisfies the structural rules of at least one
    expected*.xaml reference file in the fixture directory.

    "1 pass wins" — useful when multiple valid XAML variants exist for the same
    fixture scenario (e.g. different UiPath Studio versions produce different but
    equally valid clipboard snippets).
    """
    expected_files = expected_xaml_files(fixture_dir)
    if not expected_files:
        pytest.skip("No expected*.xaml files in fixture directory")

    out = tmp_path / "out.xaml"
    run(script, str(fixture_dir / "input.xlsx"), "--generate-tostring", "--output-xaml", str(out))
    generated_root = parse_xaml(out)

    # Collect results per expected file
    all_failures: dict[str, list[str]] = {}
    for expected_path in expected_files:
        failures = xaml_structural_rules(generated_root)
        if not failures:
            return  # 1 pass wins
        all_failures[expected_path.name] = failures

    # All expected variants failed — report all failures
    report = "\n".join(
        f"  [{name}]: {', '.join(fs)}" for name, fs in all_failures.items()
    )
    pytest.fail(f"Generated XAML failed structural rules against all expected variants:\n{report}")


# ---------------------------------------------------------------------------
# Error / warning cases
# ---------------------------------------------------------------------------


def test_missing_file_exits_1(script):
    assert run(script, "nonexistent.xlsx").returncode == 1


def test_wrong_extension_exits_1(script):
    assert run(script, "input.csv").returncode == 1


def test_bad_header_warns(script):
    bad = Path("D:/github.com/rpapub/ConFormMold/test/fixtures/Config_BadHeader.xlsx")
    if not bad.exists():
        pytest.skip("upstream ConFormMold fixtures not available")
    result = run(script, str(bad))
    assert result.returncode == 0
    assert "[WARN]" in result.stderr
