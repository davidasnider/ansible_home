import sys
import urllib.request
import json
import yaml
from concurrent.futures import ThreadPoolExecutor
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

# Bounded wait for api.github.com: without a timeout, urlopen() falls back to the
# socket global default (None here) and a single stalled connection would hang the
# CI job forever instead of failing with exit code 2.
HTTP_TIMEOUT_SECONDS = 30

def get_latest_version(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ansible-home-update-checker"}
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as res:
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

    # The two release lookups are independent, so fetch them concurrently: the
    # script then waits for the slower call instead of their sum (worst case is
    # one 30s timeout, not two). Results are read back in the original order,
    # and a failure still surfaces as SystemExit(2) from .result().
    with ThreadPoolExecutor(max_workers=2) as pool:
        remote_future = pool.submit(get_latest_version, "custom-components/remote_homeassistant")
        home_assistant_future = pool.submit(get_latest_version, "home-assistant/core")
        latest_remote = remote_future.result()
        latest_ha = home_assistant_future.result()

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
