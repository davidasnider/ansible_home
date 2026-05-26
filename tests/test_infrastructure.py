import pytest
import runpy

@pytest.mark.unit
def test_missing_github_token_raises_error():
    """Test that missing GITHUB_TOKEN environment variable raises a ValueError."""
    with pytest.MonkeyPatch.context() as m:
        m.delenv("GITHUB_TOKEN", raising=False)

        with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
            runpy.run_path("infrastructure/__main__.py")
