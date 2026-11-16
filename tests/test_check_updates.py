import importlib.util
from pathlib import Path
import socket
import sys
from unittest.mock import patch
import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts/check_updates.py"
spec = importlib.util.spec_from_file_location("check_updates", SCRIPT_PATH)
check_updates = importlib.util.module_from_spec(spec)
sys.modules["check_updates"] = check_updates
spec.loader.exec_module(check_updates)


def test_main_all_up_to_date(capsys):
    mock_versions = {
        "remote_homeassistant": "4.6",
        "home_assistant": "2026.8.1",
    }
    with patch.object(check_updates, "get_current_versions", return_value=mock_versions):
        with patch.object(
            check_updates,
            "get_latest_version",
            side_effect=lambda repo: "4.6" if "remote_homeassistant" in repo else "2026.8.1",
        ):
            with pytest.raises(SystemExit) as exc_info:
                check_updates.main()

            assert exc_info.value.code == 0

    captured = capsys.readouterr()
    assert "✅ remote_homeassistant: 4.6 (up to date)" in captured.out
    assert "✅ home_assistant: 2026.8.1 (up to date)" in captured.out
    assert "✨ All dependencies are up to date." in captured.out
    assert "roles/home_assistant_remote/defaults/main.yml" in captured.out


def test_main_update_available(capsys):
    mock_versions = {
        "remote_homeassistant": "4.6",
        "home_assistant": "2026.8.1",
    }
    with patch.object(check_updates, "get_current_versions", return_value=mock_versions):
        with patch.object(
            check_updates,
            "get_latest_version",
            side_effect=lambda repo: "4.7" if "remote_homeassistant" in repo else "2026.10.4",
        ):
            with pytest.raises(SystemExit) as exc_info:
                check_updates.main()

            assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "🚨 remote_homeassistant: 4.6 -> 4.7 (update available)" in captured.out
    assert "🚨 home_assistant: 2026.8.1 -> 2026.10.4 (update available)" in captured.out
    assert "💡 Actionable next steps:" in captured.out
    assert 'home_assistant_remote_version: "4.7"' in captured.out
    assert 'home_assistant_remote_ha_version: "2026.10.4"' in captured.out
    assert "roles/home_assistant_remote/defaults/main.yml" in captured.out


class _FakeGitHubResponse:
    """Minimal stand-in for the object that urllib.request.urlopen returns."""

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    def read(self):
        return b'{"tag_name": "v4.6"}'


def test_get_latest_version_passes_a_network_timeout():
    """The api.github.com call must get a finite timeout: without one, urlopen()
    falls back to the socket global default (None) and a single stalled
    connection would hang the CI job forever instead of failing."""
    with patch.object(check_updates.urllib.request, "urlopen", return_value=_FakeGitHubResponse()) as mock_urlopen:
        version = check_updates.get_latest_version("custom-components/remote_homeassistant")

    assert version == "4.6"
    mock_urlopen.assert_called_once()
    kwargs = mock_urlopen.call_args.kwargs
    assert "timeout" in kwargs, f"urlopen must specify a timeout; got: {mock_urlopen.call_args}"
    assert kwargs["timeout"] > 0


def test_get_latest_version_fails_fast_on_timeout():
    """A stalled connection (socket.timeout) must surface as the normal error
    exit code 2, not a process that never finishes."""
    with patch.object(check_updates.urllib.request, "urlopen", side_effect=socket.timeout("timed out")):
        with pytest.raises(SystemExit) as exc_info:
            check_updates.get_latest_version("home-assistant/core")

    assert exc_info.value.code == 2
