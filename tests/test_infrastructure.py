import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

_TEST_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _TEST_DIR.parent


@pytest.mark.unit
def test_missing_github_token_raises_error():
    """Test that missing GITHUB_TOKEN environment variable raises a ValueError.

    Uses a subprocess so the test is fully isolated:
    - No local .env file is discovered (the script runs in a temp dir).
    - The GITHUB_TOKEN is explicitly unset in the subprocess env.
    """
    main_module = _PROJECT_ROOT / "infrastructure" / "__main__.py"

    # Start from a clean env (no GITHUB_TOKEN).
    clean_env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
    # Explicitly set GITHUB_TOKEN to empty string to ensure python-dotenv doesn't load it
    # from a local .env file when load_dotenv() is called in infrastructure/__main__.py
    clean_env["GITHUB_TOKEN"] = ""

    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [sys.executable, str(main_module)],
            capture_output=True,
            text=True,
            env=clean_env,
            cwd=tmp_dir,
        )

        assert result.returncode != 0, (
            f"Expected ValueError but script succeeded. stderr: {result.stderr}"
        )
        assert "GITHUB_TOKEN environment variable is required" in result.stderr
