import runpy
import pytest
from pathlib import Path


@pytest.mark.unit
def test_missing_github_token_raises_error(tmp_path, monkeypatch):
    """Test that missing GITHUB_TOKEN environment variable raises a ValueError."""
    # Derive the absolute path to infrastructure/__main__.py from this file's location
    script_path = Path(__file__).resolve().parent.parent / "infrastructure/__main__.py"

    # Run from a temp directory so load_dotenv() won't discover a local .env
    # in the repo root, and the absolute script path ensures CWD doesn't matter.
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
        runpy.run_path(str(script_path), run_name="__main__")
