from pathlib import Path
import pytest

SKILL_ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"

# CLI flags used to produce the reframework-v23.10.0 fixture set:
#   --generate-tostring
#   (all other flags at defaults)


@pytest.fixture
def fixture_dir():
    return FIXTURES / "reframework-v23.10.0"
