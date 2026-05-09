"""Convert Outlook .msg files to markdown.

Attachment content is not harvested. Filenames are listed for reference only.
"""

from pathlib import Path


def convert(src: Path, dst: Path) -> None:
    import extract_msg

    with extract_msg.openMsg(str(src)) as msg:
        subject = msg.subject or "(no subject)"
        lines: list[str] = [
            f"# {subject}",
            "",
            f"**From:** {msg.sender or ''}",
            f"**To:** {msg.to or ''}",
        ]
        if msg.cc:
            lines.append(f"**CC:** {msg.cc}")
        lines += [
            f"**Date:** {msg.date or ''}",
            "",
            "---",
            "",
            (msg.body or "").strip(),
        ]
        if msg.attachments:
            lines += ["", "---", "", "## Attachments", ""]
            for att in msg.attachments:
                name = att.longFilename or att.shortFilename or "(unnamed)"
                lines.append(f"- {name}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines), encoding="utf-8")
