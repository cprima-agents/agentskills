#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""
UiPath Studio Execution Log Parser

Parses local UiPath execution logs, groups entries by job run (jobId),
and summarises each run with level counts and error details.

Usage:
    uv run parse_logs.py
    uv run parse_logs.py --days 3
    uv run parse_logs.py --date 2026-03-24
    uv run parse_logs.py --process BlankProcess --errors-only
    uv run parse_logs.py --list-files
    uv run parse_logs.py --format json --all

Convenience utilities (no log files required):
    uv run parse_logs.py --duration "08:35:14.6902 Info {...}" "08:35:22.9335 Error {...}"

Exit codes:
    0  success (including "no runs found" with filters)
    1  input error (file not found, unparseable timestamp)
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Common UiPath execution log locations on Windows (user-level and service-level)
LOG_LOCATIONS = [
    Path.home() / "AppData/Local/UiPath/Logs",
    Path("C:/ProgramData/UiPath/Logs"),
]
# Note: %USERPROFILE%\.uipath\ is NOT a known log location and is not searched.

# Each log line: "HH:MM:SS.NNNN Level {...json...}"
LOG_LINE_RE = re.compile(
    r"^(?P<time>\d{2}:\d{2}:\d{2}\.\d+)\s+(?P<level_prefix>\w+)\s+(?P<json>\{.+\})$"
)

LEVEL_ORDER = {
    "Trace": 0,
    "Verbose": 1,
    "Information": 2,
    "Warning": 3,
    "Error": 4,
    "Fatal": 5,
}


def extract_timestamp(log_line: str) -> datetime | None:
    """
    Extract a timezone-aware datetime from a raw UiPath log line.

    Tries the JSON 'timeStamp' field first (full ISO-8601 with timezone),
    falls back to the HH:MM:SS prefix (no date, no tz — same-day only).
    """
    m = LOG_LINE_RE.match(log_line.strip().lstrip("\ufeff"))
    if m:
        try:
            data = json.loads(m.group("json"))
            ts = data.get("timeStamp")
            if ts:
                # Python 3.11+ handles colon-less tz offset; fromisoformat is robust enough here
                return datetime.fromisoformat(ts)
        except (json.JSONDecodeError, ValueError):
            pass
        # Fallback: time prefix only, treat as today, no timezone
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return datetime.fromisoformat(f"{today}T{m.group('time')}")
        except ValueError:
            pass
    return None


def cmd_duration(lines: list[str]) -> None:
    """Calculate and print the duration between two log lines."""
    if len(lines) != 2:
        print("Error: --duration requires exactly 2 log lines.", file=sys.stderr)
        sys.exit(1)

    t0 = extract_timestamp(lines[0])
    t1 = extract_timestamp(lines[1])

    if t0 is None:
        print("Error: could not parse timestamp from first line.", file=sys.stderr)
        sys.exit(1)
    if t1 is None:
        print("Error: could not parse timestamp from second line.", file=sys.stderr)
        sys.exit(1)

    # Ensure both are comparable (strip tz if only one has it)
    if t0.tzinfo and t1.tzinfo:
        delta = abs(t1 - t0)
    else:
        delta = abs(t1.replace(tzinfo=None) - t0.replace(tzinfo=None))

    total_seconds = delta.total_seconds()
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    ms = int((total_seconds - int(total_seconds)) * 1000)

    print(f"From : {t0.isoformat()}")
    print(f"To   : {t1.isoformat()}")
    if hours:
        print(f"Delta: {hours}h {minutes}m {seconds}.{ms:03d}s")
    elif minutes:
        print(f"Delta: {minutes}m {seconds}.{ms:03d}s")
    else:
        print(f"Delta: {seconds}.{ms:03d}s  ({total_seconds:.3f} seconds total)")


def find_execution_log_files(days: int = 7, locations: list[Path] | None = None) -> list[Path]:
    """Discover *_Execution.log files modified within the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    files: list[Path] = []
    for loc in locations or LOG_LOCATIONS:
        if not loc.exists():
            continue
        for f in sorted(loc.glob("*_Execution.log")):
            try:
                file_date = datetime.strptime(f.name[:10], "%Y-%m-%d")
                if file_date >= cutoff:
                    files.append(f)
            except ValueError:
                continue
    return sorted(files)


def parse_log_file(path: Path) -> list[dict]:
    """Parse a single execution log file into a list of structured entries."""
    entries: list[dict] = []
    try:
        with open(path, encoding="utf-8-sig") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.rstrip()
                m = LOG_LINE_RE.match(line)
                if not m:
                    continue
                try:
                    data = json.loads(m.group("json"))
                    data["_source_file"] = str(path)
                    data["_lineno"] = lineno
                    entries.append(data)
                except json.JSONDecodeError:
                    continue
    except OSError as exc:
        print(f"  [warn] Cannot read {path}: {exc}", file=sys.stderr)
    return entries


def group_by_job(entries: list[dict]) -> dict[str, list[dict]]:
    """Group log entries by jobId; entries without a jobId go into 'unknown'."""
    jobs: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        jobs[entry.get("jobId", "unknown")].append(entry)
    return dict(jobs)


def summarise_job(job_id: str, entries: list[dict]) -> dict:
    """Build a summary dict for a single job run."""
    first = entries[0]
    last = entries[-1]

    counts: dict[str, int] = defaultdict(int)
    errors: list[dict] = []
    warnings: list[dict] = []

    for entry in entries:
        level = entry.get("level", "Unknown")
        counts[level] += 1
        if level in ("Error", "Fatal"):
            errors.append(entry)
        elif level == "Warning":
            warnings.append(entry)

    ended_normally = "execution ended" in last.get("message", "").lower()
    has_errors = bool(errors)

    if ended_normally and not has_errors:
        status = "ok"
    elif ended_normally and has_errors:
        status = "fail"
    else:
        status = "open"  # no end message: still running, interrupted, or log truncated

    return {
        "jobId": job_id,
        "processName": first.get("processName", "?"),
        "processVersion": first.get("processVersion", "?"),
        "initiatedBy": first.get("initiatedBy", "?"),
        "robotName": first.get("robotName", "?"),
        "machineName": first.get("machineName", "?"),
        "start": first.get("timeStamp", ""),
        "end": last.get("timeStamp", ""),
        "duration": last.get("totalExecutionTime"),
        "durationSec": last.get("totalExecutionTimeInSeconds"),
        "status": status,
        "counts": dict(counts),
        "errors": errors,
        "warnings": warnings,
        "_entries": entries,
    }


def _level_badge(counts: dict[str, int]) -> str:
    """Short counts string, e.g. '12 Info  2 Warn  1 Error'."""
    parts = []
    for level in ("Trace", "Verbose", "Information", "Warning", "Error", "Fatal"):
        n = counts.get(level, 0)
        if n:
            parts.append(f"{n} {level[:4]}")
    return "  ".join(parts) if parts else "—"


def print_report(summaries: list[dict], show_warnings: bool = False) -> None:
    """Print a developer-oriented terminal report."""
    for s in summaries:
        flag = {"ok": " OK ", "fail": "FAIL", "open": " .. "}.get(s["status"], " ?? ")
        start = s["start"][:19].replace("T", " ") if s["start"] else "?"
        duration = s["duration"] or (
            f"{s['durationSec']}s" if s["durationSec"] is not None else "?"
        )

        print(f"\n[{flag}] {start}  {s['processName']} v{s['processVersion']}")
        print(f"       Job      : {s['jobId']}")
        print(f"       Initiated: {s['initiatedBy']}  |  Robot: {s['robotName']}")
        print(f"       Duration : {duration}")
        print(f"       Levels   : {_level_badge(s['counts'])}")

        if s["errors"]:
            print(f"       Errors ({len(s['errors'])}):")
            for e in s["errors"]:
                ts = e.get("timeStamp", "")[:19].replace("T", " ")
                msg = e.get("message", "").replace("\r\n", " | ").replace("\n", " | ")
                print(f"         [{ts}] {e.get('fileName', '?')}: {msg[:300]}")

        if show_warnings and s["warnings"]:
            print(f"       Warnings ({len(s['warnings'])}):")
            for w in s["warnings"]:
                ts = w.get("timeStamp", "")[:19].replace("T", " ")
                msg = w.get("message", "").replace("\r\n", " | ")
                print(f"         [{ts}] {msg[:200]}")

        needle = s.get("_needle")
        if needle:
            needle_lc = needle.lower()
            matches = [e for e in s.get("_entries", [])
                       if needle_lc in e.get("message", "").lower()]
            print(f"       Needle '{needle}' ({len(matches)} match(es)):")
            for e in matches:
                ts = e.get("timeStamp", "")[:19].replace("T", " ")
                msg = e.get("message", "").replace("\r\n", " | ")
                print(f"         [{ts}] {e.get('level','?'):11s} {msg[:300]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse UiPath Studio local execution logs, grouped by job run."
    )
    parser.add_argument(
        "--days", type=int, default=7,
        help="Look back N days for log files (default: 7)"
    )
    parser.add_argument(
        "--date", metavar="YYYY-MM-DD",
        help="Show only runs from a specific date"
    )
    parser.add_argument(
        "--process", metavar="NAME",
        help="Filter by process name (case-insensitive substring)"
    )
    parser.add_argument(
        "--duration", nargs=2, metavar=("LINE1", "LINE2"),
        help="Calculate duration between two raw log lines (no files needed)"
    )
    parser.add_argument(
        "--needle", metavar="TEXT",
        help="Show only runs containing TEXT in any log message (case-insensitive)"
    )
    parser.add_argument(
        "--errors-only", action="store_true",
        help="Show only runs that contain errors"
    )
    parser.add_argument(
        "--warnings", action="store_true",
        help="Also print warning details (not just errors)"
    )
    parser.add_argument(
        "--last", type=int, default=1, metavar="N",
        help="Show the last N job runs (default: 1, i.e. most recent only)"
    )
    parser.add_argument(
        "--all", dest="show_all", action="store_true",
        help="Show all job runs (overrides --last)"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format: text (default) or json. JSON sends data to stdout, diagnostics to stderr."
    )
    parser.add_argument(
        "--list-files", action="store_true",
        help="List discovered log files and exit"
    )
    parser.add_argument(
        "--log-dir", metavar="PATH",
        help="Override log directory (use instead of auto-discovery)"
    )
    parser.add_argument(
        "--file", metavar="PATH",
        help="Parse a specific log file directly (skips all discovery and date filters)"
    )
    args = parser.parse_args()

    # --- convenience utilities (no log files required) ---
    if args.duration:
        cmd_duration(args.duration)
        return

    if args.file:
        files = [Path(args.file)]
        if not files[0].exists():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        if not args.show_all and args.last == 1:
            args.show_all = True  # show all runs when a file is explicitly provided
    else:
        locations = [Path(args.log_dir)] if args.log_dir else None
        files = find_execution_log_files(days=args.days, locations=locations)

        if args.date:
            files = [f for f in files if f.name.startswith(args.date)]

    if args.list_files:
        if not files:
            print("No execution log files found.")
        for f in files:
            print(f)
        return

    if not files:
        print(
            f"No execution log files found in the last {args.days} day(s). "
            "Use --log-dir or --file to specify a path.",
            file=sys.stderr,
        )
        sys.exit(0)

    all_entries: list[dict] = []
    for f in files:
        all_entries.extend(parse_log_file(f))

    jobs = group_by_job(all_entries)
    summaries = [summarise_job(jid, entries) for jid, entries in jobs.items()]
    summaries.sort(key=lambda s: s["start"])

    if args.process:
        summaries = [s for s in summaries
                     if args.process.lower() in s["processName"].lower()]

    if args.needle:
        needle_lc = args.needle.lower()
        summaries = [s for s in summaries
                     if any(needle_lc in e.get("message", "").lower()
                            for e in s.get("_entries", []))]
        # attach needle for highlighting in report
        for s in summaries:
            s["_needle"] = args.needle

    if args.errors_only:
        summaries = [s for s in summaries if s["errors"]]

    if not summaries:
        print("No matching runs found.", file=sys.stderr)
        sys.exit(0)

    total = len(summaries)
    if not args.show_all:
        summaries = summaries[-args.last:]

    shown = len(summaries)

    if args.format == "json":
        # Strip internal private keys before serialising
        _PRIVATE = {"_entries", "_needle"}
        def _clean(s: dict) -> dict:
            return {k: v for k, v in s.items() if k not in _PRIVATE}
        print(json.dumps([_clean(s) for s in summaries], indent=2, default=str))
    else:
        hint = "" if args.show_all else " (use --last N or --all to see more)"
        print(
            f"UiPath Execution Log - showing {shown} of {total} run(s)"
            f" from {len(files)} file(s){hint}",
            file=sys.stderr,
        )
        print_report(summaries, show_warnings=args.warnings)
        print()


if __name__ == "__main__":
    main()
