#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "python-docx>=0.8",
#   "pypdf>=4.0",
#   "openpyxl>=3.1",
#   "xlrd>=2.0",
#   "extract-msg>=0.37",
# ]
# ///
"""Harvest mixed-format files from one or more folders into sibling _harvested/ folders.

Conversion is determined only by file extension. Hints label folders for
interpretation by a subsequent reading or elicitation skill — they never
affect which converter is used or how files are transformed.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from converters import docx_to_md, images, msg_to_md, pdf_to_md, xlsx_to_md

# ---------------------------------------------------------------------------
# Extension dispatch table
# ---------------------------------------------------------------------------

EXT_MAP: dict[str, tuple[str, str, object]] = {
    ".msg":  ("mails",  "email_message", msg_to_md.convert),
    ".docx": ("docs",   "word_document", docx_to_md.convert),
    ".pdf":  ("docs",   "pdf_document",  pdf_to_md.convert),
    ".xlsx": ("sheets", "spreadsheet",   xlsx_to_md.convert),
    ".xls":  ("sheets", "spreadsheet",   xlsx_to_md.convert),
    ".png":  ("images", "image",         images.convert),
    ".jpg":  ("images", "image",         images.convert),
    ".jpeg": ("images", "image",         images.convert),
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def make_output_folder(source: Path) -> Path:
    base = source.parent / (source.name + "_harvested")
    if not base.exists():
        return base
    n = 2
    while True:
        candidate = source.parent / (source.name + f"_harvested_{n}")
        if not candidate.exists():
            return candidate
        n += 1


def output_path(src: Path, source_root: Path, out_root: Path, category: str, suffix: str) -> Path:
    rel = src.relative_to(source_root)
    return out_root / category / rel.with_name(src.name + suffix)


def to_posix(p: Path) -> str:
    return p.as_posix()


def to_posix_abs(p: Path) -> str:
    return p.resolve().as_posix()


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------------------
# Skip logic
# ---------------------------------------------------------------------------


def should_skip(path: Path) -> bool:
    if path.is_dir():
        return True
    if any(part.endswith("_harvested") or "_harvested_" in part for part in path.parts):
        return True
    if path.name.startswith("~$"):
        return True
    if path.name.startswith("."):
        return True
    return False


# ---------------------------------------------------------------------------
# Inventory text
# ---------------------------------------------------------------------------


def _build_inventory(
    folder: Path,
    out_folder: Path,
    hint: str | None,
    entries: list[dict],
    unsupported: list[str],
) -> str:
    lines = [
        f"# Harvest inventory",
        "",
        f"**Source:** `{folder}`  ",
        f"**Output:** `{out_folder}`  ",
        f"**Hint:** {hint or '*(none)*'}",
        "",
        "## Converted files",
        "",
        "| Source | Kind | Output | Status |",
        "| --- | --- | --- | --- |",
    ]
    for e in entries:
        lines.append(f"| {md_escape(e['source'])} | {e['kind']} | {md_escape(e['output'])} | {e['status']} |")

    if unsupported:
        lines += ["", "## Unsupported files (skipped)", ""]
        for u in unsupported:
            lines.append(f"- {u}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Core harvest logic
# ---------------------------------------------------------------------------


def harvest_folder(
    folder: Path,
    hint: str | None,
    recursive: bool,
    dry_run: bool,
) -> None:
    out_folder = make_output_folder(folder)

    glob = folder.rglob("*") if recursive else folder.glob("*")
    all_paths = sorted(p for p in glob if not p.is_dir())

    entries: list[dict] = []
    unsupported: list[str] = []

    for src in all_paths:
        if should_skip(src):
            continue

        ext = src.suffix.lower()
        rel_src = to_posix(src.relative_to(folder))

        if ext not in EXT_MAP:
            unsupported.append(rel_src)
            continue

        category, kind, converter = EXT_MAP[ext]
        suffix = "" if ext in IMAGE_EXTS else ".md"
        dst = output_path(src, folder, out_folder, category, suffix)
        rel_dst = to_posix(dst.relative_to(out_folder))

        entry: dict = {
            "source": rel_src,
            "extension": ext,
            "output": rel_dst,
            "kind": kind,
        }

        if dry_run:
            status = "copied" if ext in IMAGE_EXTS else "ok"
            entry["status"] = status
            entries.append(entry)
            continue

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            converter(src, dst)  # type: ignore[call-arg]
            entry["status"] = "copied" if ext in IMAGE_EXTS else "ok"
        except Exception as exc:
            entry["status"] = "error"
            entry["error"] = str(exc)

        entries.append(entry)

    # Sort for deterministic output
    entries.sort(key=lambda e: e["source"])
    unsupported.sort()

    if dry_run:
        print(f"\n[DRY RUN] Source:  {folder}")
        print(f"[DRY RUN] Output:  {out_folder}")
        print(f"[DRY RUN] Hint:    {hint or 'null'}")
        print(f"[DRY RUN] Files:   {len(entries)} supported, {len(unsupported)} unsupported")
        for e in entries:
            print(f"  {e['source']} -> {e['output']} ({e['kind']})")
        if unsupported:
            print("  Unsupported:")
            for u in unsupported:
                print(f"    {u}")
        return

    # Write outputs
    out_folder.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "recursive": recursive,
        "source_folder": to_posix_abs(folder),
        "hint": hint,
        "output_folder": to_posix_abs(out_folder),
        "files": entries,
        "unsupported": unsupported,
    }
    (out_folder / "inventory.md").write_text(
        _build_inventory(folder, out_folder, hint, entries, unsupported),
        encoding="utf-8",
    )

    ok = sum(1 for e in entries if e["status"] == "ok")
    copied = sum(1 for e in entries if e["status"] == "copied")
    errors = sum(1 for e in entries if e["status"] == "error")
    stats = {"ok": ok, "copied": copied, "error": errors, "unsupported": len(unsupported)}
    manifest["stats"] = stats
    (out_folder / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Harvested: {folder.name} -> {out_folder.name}")
    print(f"  {ok} converted, {copied} copied, {errors} errors, {len(unsupported)} unsupported")
    if errors:
        for e in entries:
            if e["status"] == "error":
                print(f"  ERROR {e['source']}: {e.get('error', '')}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_hint(value: str) -> tuple[str, str]:
    if "=" not in value:
        print(f"ERROR: --hint must be FOLDER=LABEL, got: {value}", file=sys.stderr)
        sys.exit(1)
    folder, _, label = value.partition("=")
    return str(Path(folder).resolve()), label


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("folders", nargs="+", help="Source folder(s) to harvest")
    parser.add_argument(
        "--hint",
        metavar="FOLDER=LABEL",
        action="append",
        default=[],
        help="Label for a folder (interpretation only, repeatable)",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Process top-level files only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing any files",
    )
    args = parser.parse_args()

    hints: dict[str, str] = {}
    for h in args.hint:
        k, v = _parse_hint(h)
        hints[k] = v

    for raw in args.folders:
        p = Path(raw).resolve()
        if not p.exists():
            print(f"ERROR: folder does not exist: {raw}", file=sys.stderr)
            sys.exit(1)
        if not p.is_dir():
            print(f"ERROR: path is a file, not a folder: {raw}", file=sys.stderr)
            sys.exit(1)

        hint = hints.get(str(p))
        harvest_folder(
            folder=p,
            hint=hint,
            recursive=not args.no_recursive,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
