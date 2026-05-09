---
name: folder-harvest
description: >
  Convert mixed-format files in one or more source folders into markdown-ready
  output for reading, analysis, or elicitation. Produces a sibling
  <foldername>_harvested/ folder containing manifest.json, inventory.md,
  and converted files organised by type. Converts .msg, .docx, .pdf, .xlsx/.xls
  by extension; copies images as-is. Use when the user points at a folder of
  source files and wants them prepared for later analysis — e.g. "harvest this
  testdata folder", "convert these docs for reading", "prepare these mails for
  analysis", or "I have a folder of mixed files, read them".
license: Apache-2.0
compatibility: Windows, macOS, Linux (requires Python 3.11+, uv)
metadata:
  author: Christian Prior-Mamulyan
  version: 0.1.0
allowed-tools: Bash
---

# folder-harvest

> **Rule:** Hints describe folder context for interpretation only. They must never
> affect which converter is used or how any file is transformed.

## Invocation

```bash
uv run skills/folder-harvest/scripts/harvest.py <folder> [<folder> ...] \
  [--hint <folder>=<label>] [--no-recursive] [--dry-run]
```

Examples:

```bash
# Single folder with a hint
uv run skills/folder-harvest/scripts/harvest.py ./testdata --hint ./testdata=testdata

# Multiple folders
uv run skills/folder-harvest/scripts/harvest.py ./mails ./docs \
  --hint ./mails=emails --hint ./docs=process-docs

# Flat (top-level files only)
uv run skills/folder-harvest/scripts/harvest.py ./testdata --no-recursive

# Preview without writing
uv run skills/folder-harvest/scripts/harvest.py ./testdata --dry-run
```

## Supported formats

| Extension | Category | Kind | Notes |
| --- | --- | --- | --- |
| `.msg` | `mails` | `email_message` | Attachments listed, not extracted |
| `.docx` | `docs` | `word_document` | Paragraphs + tables; no images/OLE |
| `.pdf` | `docs` | `pdf_document` | Text only; no OCR for scanned pages |
| `.xlsx` | `sheets` | `spreadsheet` | Cached values; capped at 500 rows/sheet |
| `.xls` | `sheets` | `spreadsheet` | Same output contract as .xlsx |
| `.png` `.jpg` `.jpeg` | `images` | `image` | Copied as-is |

## Output structure

```
<source_name>_harvested/
├── manifest.json       ← machine-readable contract (schema_version: 1)
├── inventory.md        ← human-readable table of all files
├── mails/
│   └── subdir/example.msg.md
├── docs/
│   ├── brief.docx.md
│   └── subdir/policy.pdf.md
├── sheets/
│   └── cases.xlsx.md
└── images/
    └── screenshot.png
```

Collision: if `<source>_harvested/` already exists, the new folder is named
`<source>_harvested_2`, `_harvested_3`, etc.

## Known limitations

- **No OCR:** scanned PDFs and image-only pages produce empty or partial text.
- **Attachments:** `.msg` attachment filenames are listed; content is not extracted.
- **Dotfiles skipped:** files starting with `.` are skipped. Windows hidden-attribute
  files are not detected in v0.1.
- **Office temp files skipped:** files starting with `~$` are skipped.
- **Folders inside `*_harvested*`:** skipped to avoid processing prior output.

## After harvesting

Summarise for the user:

- Source folders harvested
- Output folder(s) created
- File counts by extension
- Any errors or unsupported files

Then ask: "Shall I read the harvested folder now?" — or proceed directly if the
user's intent implies it.
