import sys
import urllib.request
import json
import yaml
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULTS_FILE = REPO_ROOT / "roles/home_assistant_remote/defaults/main.yml"
DEFAULTS_REL = DEFAULTS_FILE.relative_to(REPO_ROOT)

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

    print(f"Checking dependencies against {DEFAULTS_REL}...")

    updates = []
    checks = [
        ("remote_homeassistant", "home_assistant_remote_version", current["remote_homeassistant"], latest_remote),
        ("home_assistant", "home_assistant_remote_ha_version", current["home_assistant"], latest_ha),
    ]

    for name, key, pinned, latest in checks:
        if pinned == latest:
            print(f"  ✅ {name}: {pinned} (up to date)")
        else:
            print(f"  🚨 {name}: {pinned} -> {latest} (update available)")
            updates.append((name, key, pinned, latest))

    if updates:
        print("\n💡 Actionable next steps:")
        print(f"   Update the pinned versions in '{DEFAULTS_REL}':")
        for _, key, _, latest in updates:
            print(f"     {key}: \"{latest}\"")
        # Exit with code 1 to indicate an update is available (triggers CI failure/email notification)
        sys.exit(1)
    else:
        print("\n✨ All dependencies are up to date.")
        sys.exit(0)

if __name__ == "__main__":
    main()
