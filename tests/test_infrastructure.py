import os
import pytest
import subprocess
import sys
from pathlib import Path

@pytest.mark.unit
def test_missing_github_token_raises_error(tmp_path, monkeypatch):
    """Test that missing GITHUB_TOKEN environment variable raises an error."""
    script_path = Path(__file__).resolve().parent.parent / "infrastructure/__main__.py"

    # Remove GITHUB_TOKEN from environment if it exists
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    env = os.environ.copy()
    # Explicitly set to empty string so load_dotenv() won't populate it from .env files
    # (load_dotenv does not overwrite existing environment variables by default)
    env["GITHUB_TOKEN"] = ""

    # Execute the file as a subprocess from a temporary directory for strict environment isolation
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0
    assert "GITHUB_TOKEN environment variable is required" in result.stderr

@pytest.mark.unit
def test_missing_github_token_raises_value_error_in_process(tmp_path, monkeypatch):
    """Test that missing GITHUB_TOKEN environment variable raises an error during import."""
    # Ensure the module is reloaded if already imported, using monkeypatch for cleanup
    monkeypatch.delitem(sys.modules, "infrastructure", raising=False)
    monkeypatch.delitem(sys.modules, "infrastructure.__main__", raising=False)

    # Remove GITHUB_TOKEN from environment if it exists
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    # Run the import from tmp_path to prevent accidental .env discovery in working directory
    monkeypatch.chdir(tmp_path)

    # Add root dir to sys.path to resolve infrastructure module safely using monkeypatch
    root_dir = str(Path(__file__).resolve().parent.parent)
    monkeypatch.syspath_prepend(root_dir)

    with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
        monkeypatch.setattr('dotenv.load_dotenv', lambda *args, **kwargs: None)
        import infrastructure.__main__

    # Explicitly remove the module from sys.modules to prevent partial import leakage
    sys.modules.pop("infrastructure.__main__", None)
    sys.modules.pop("infrastructure", None)
