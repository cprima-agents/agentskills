"""Copy image files as-is into the output location."""

import shutil
from pathlib import Path


def convert(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
