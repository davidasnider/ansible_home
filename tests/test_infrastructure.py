import os
import pytest
import subprocess
import sys
from pathlib import Path

@pytest.mark.unit
def test_missing_github_token_raises_error(tmp_path):
    """Test that missing GITHUB_TOKEN environment variable raises a ValueError."""
    # 1. Absolute path to the script
    repo_root = Path(__file__).resolve().parent.parent
    main_file = repo_root / "infrastructure" / "__main__.py"

    # 2. .env and env isolation: Copy environment but remove GITHUB_TOKEN
    env = os.environ.copy()
    if "GITHUB_TOKEN" in env:
        del env["GITHUB_TOKEN"]

    # 3. CWD isolation: Run subprocess from temporary directory
    # Using python executable directly so it processes the script
    result = subprocess.run(
        [sys.executable, str(main_file)],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0
    assert "ValueError: GITHUB_TOKEN environment variable is required" in result.stderr
