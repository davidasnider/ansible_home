"""Static guard: every get_url task in the workstation provisioning files must set a timeout.

ansible.builtin.get_url has no default socket timeout: without an explicit
`timeout:` a stalled connection to the remote host (or any on-path interference)
hangs the whole playbook run forever, with no failure path and no retry. The
Hermes installer task in local-mac.yml already pins `timeout: 300`; this test
keeps every other remote fetch in the workstation role on the same bounded wait.

Run with: uv run pytest tests/ -k get_url_timeouts
"""

from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.unit]

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSTATION_TASKS_DIR = REPO_ROOT / "roles" / "workstation" / "tasks"

TASK_FILES = [
    WORKSTATION_TASKS_DIR / "local-mac.yml",
    WORKSTATION_TASKS_DIR / "local-linux-packages.yml",
    WORKSTATION_TASKS_DIR / "local-linux-shell.yml",
]


def _walk_actions(nodes):
    """Yield (task_name, action_dict) for every task in a (possibly nested) list."""
    if nodes is None:
        return
    for node in nodes:
        if not isinstance(node, dict):
            continue
        # A task is any mapping that names an Ansible action (module keyword).
        if "name" in node and any(key for key in node if key not in ("name",)):
            action = {key: value for key, value in node.items() if key not in ("name",)}
            yield node["name"], action
        # Recurse into block/always/rescue and any task lists so nested tasks count.
        for section in ("block", "always", "rescue"):
            if isinstance(node.get(section), list):
                yield from _walk_actions(node[section])


def _get_url_tasks(path):
    """All (task_name, get_url parameters) pairs in one tasks file."""
    tasks = yaml.safe_load(path.read_text())
    found = []
    for name, action in _walk_actions(tasks):
        if "ansible.builtin.get_url" in action:
            params = dict(action["ansible.builtin.get_url"])
            found.append((name, path.name, params))
    return found


def _all_get_url_tasks():
    seen = []
    for path in TASK_FILES:
        assert path.is_file(), f"missing tasks file: {path}"
        seen.extend(_get_url_tasks(path))
    return seen


def test_workstation_files_contain_get_url_downloads():
    """Sanity: the guard must have something to check (no silent pass on an empty set)."""
    tasks = _all_get_url_tasks()
    assert len(tasks) >= 4, f"expected the known remote fetches to be present, found: {tasks}"


def test_every_get_url_download_has_a_bounded_timeout():
    """A get_url without `timeout:` can hang the run forever; require a positive one."""
    offenders = []
    for name, filename, params in _all_get_url_tasks():
        timeout = params.get("timeout")
        if not (isinstance(timeout, int) and not isinstance(timeout, bool) and timeout > 0):
            offenders.append(f"{filename}: '{name}' (timeout={timeout!r})")
    assert not offenders, "get_url tasks without a positive timeout: " + "; ".join(offenders)
