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
