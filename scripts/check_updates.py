import sys
import urllib.request
import json
import yaml
from pathlib import Path

# Paths
DEFAULTS_FILE = Path(__file__).resolve().parent.parent / "roles/home_assistant_remote/defaults/main.yml"

def get_current_versions():
    try:
        with open(DEFAULTS_FILE, "r") as f:
            data = yaml.safe_load(f)
        return {
            "remote_homeassistant": data.get("home_assistant_remote_version"),
            "home_assistant": data.get("home_assistant_remote_ha_version")
        }
    except Exception as e:
        print(f"Error reading defaults file: {e}", file=sys.stderr)
        sys.exit(2)

def get_latest_version(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ansible-home-update-checker"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            # Github tags can sometimes start with "v", strip it if present
            return data.get("tag_name").lstrip("v")
    except Exception as e:
        print(f"Error fetching latest version for {repo}: {e}", file=sys.stderr)
        sys.exit(2)

def main():
    current = get_current_versions()
    if not current.get("remote_homeassistant") or not current.get("home_assistant"):
        print("Could not find required versions in defaults.", file=sys.stderr)
        sys.exit(2)

    latest_remote = get_latest_version("custom-components/remote_homeassistant")
    latest_ha = get_latest_version("home-assistant/core")

    print(f"remote_homeassistant: Pinned={current['remote_homeassistant']}, Latest={latest_remote}")
    print(f"home_assistant: Pinned={current['home_assistant']}, Latest={latest_ha}")

    updates_available = False

    if current['remote_homeassistant'] != latest_remote:
        print(f"🚨 UPDATE AVAILABLE: A new version ({latest_remote}) of remote_homeassistant is available!")
        updates_available = True

    if current['home_assistant'] != latest_ha:
        print(f"🚨 UPDATE AVAILABLE: A new version ({latest_ha}) of home-assistant/core is available!")
        updates_available = True

    if updates_available:
        # Exit with code 1 to indicate an update is available (triggers CI failure/email notification)
        sys.exit(1)
    else:
        print("✅ All dependencies up to date.")
        sys.exit(0)

if __name__ == "__main__":
    main()
