import sys
import urllib.request
import json
import yaml
from pathlib import Path

# Paths
DEFAULTS_FILE = Path(__file__).resolve().parent.parent / "roles/home_assistant_remote/defaults/main.yml"

def get_current_version():
    try:
        with open(DEFAULTS_FILE, "r") as f:
            data = yaml.safe_load(f)
        return data.get("home_assistant_remote_version")
    except Exception as e:
        print(f"Error reading defaults file: {e}", file=sys.stderr)
        sys.exit(2)

def get_latest_version():
    url = "https://api.github.com/repos/custom-components/remote_homeassistant/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ansible-home-update-checker"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            # Github tags can sometimes start with "v" (e.g., v4.6), strip it if present
            return data.get("tag_name").lstrip("v")
    except Exception as e:
        print(f"Error fetching latest version from GitHub: {e}", file=sys.stderr)
        sys.exit(2)

def main():
    current = get_current_version()
    if not current:
        print("Could not find 'home_assistant_remote_version' in defaults.", file=sys.stderr)
        sys.exit(2)

    latest = get_latest_version()

    print(f"Current pinned version: {current}")
    print(f"Latest available version: {latest}")

    if current != latest:
        print(f"🚨 UPDATE AVAILABLE: A new version ({latest}) of remote_homeassistant is available!")
        # Exit with code 1 to indicate an update is available (triggers CI failure/email notification)
        sys.exit(1)
    else:
        print("✅ Up to date.")
        sys.exit(0)

if __name__ == "__main__":
    main()
