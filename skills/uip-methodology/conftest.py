from __future__ import annotations

from pathlib import Path

import pytest
from ruamel.yaml import YAML as _YAML

CORPUS_DIR = Path(__file__).parent / "corpus"


@pytest.fixture(scope="session")
def corpus_dir() -> Path:
    return CORPUS_DIR


@pytest.fixture(scope="session")
def invoice_yaml(corpus_dir: Path) -> dict:
    return _YAML(typ="safe").load((corpus_dir / "invoice.yaml").read_text(encoding="utf-8"))
