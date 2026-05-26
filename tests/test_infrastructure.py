import os
import pytest
import runpy
from pathlib import Path
import dotenv

@pytest.mark.unit
def test_missing_github_token_raises_error(tmp_path, monkeypatch):
    """Test that missing GITHUB_TOKEN environment variable raises a ValueError."""
    # 1. Absolute path to the script
    repo_root = Path(__file__).resolve().parent.parent
    main_file = repo_root / "infrastructure" / "__main__.py"

    # 2. CWD isolation: ensure execution happens from a clean temporary directory
    monkeypatch.chdir(tmp_path)

    # Remove GITHUB_TOKEN from environment if it exists
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    # 3. .env isolation: patch load_dotenv so it's a no-op, preventing any .env file from repopulating
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: None)

    # Execute the file and expect ValueError
    with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
        runpy.run_path(str(main_file))
