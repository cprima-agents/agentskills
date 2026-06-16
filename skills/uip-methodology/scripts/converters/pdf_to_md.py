"""Convert PDF to markdown via text extraction.

Text extraction only. Scanned PDFs and image-only pages produce empty or partial
output. No OCR is performed.
"""

from pathlib import Path


def convert(src: Path, dst: Path) -> None:
    from pypdf import PdfReader

    reader = PdfReader(src)
    pages = []
    for i, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        pages.append(f"## Page {i}\n\n{text}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n\n---\n\n".join(pages), encoding="utf-8")
