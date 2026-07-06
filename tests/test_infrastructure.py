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
    # Ensure the module is reloaded if already imported.
    # We clear the module from sys.modules to ensure the import triggers the code execution.

    # Remove GITHUB_TOKEN from environment if it exists
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    # Run the import from tmp_path to prevent accidental .env discovery in working directory
    monkeypatch.chdir(tmp_path)

    # Add root dir to sys.path to resolve infrastructure module safely using monkeypatch
    root_dir = str(Path(__file__).resolve().parent.parent)
    monkeypatch.syspath_prepend(root_dir)

    # Capture initial state of sys.modules for restoration
    initial_modules = {k: v for k, v in sys.modules.items() if k.startswith("infrastructure")}

    try:
        # Import and assert
        monkeypatch.setattr('dotenv.load_dotenv', lambda *args, **kwargs: None)
        from importlib import import_module
        with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
            import_module("infrastructure.__main__")
    finally:
        # Restore sys.modules state
        # Remove any infrastructure modules added during the test
        for mod in list(sys.modules.keys()):
            if mod.startswith("infrastructure") and mod not in initial_modules:
                sys.modules.pop(mod, None)
        # Restore original modules
        for k, v in initial_modules.items():
            sys.modules[k] = v
