"""Integration tests for playbooks/secrets.yml (single `op inject` secrets flow).

The playbook runs in a subprocess against localhost, either with the 1Password
fetch disabled or backed by a stub `op` on PATH, so no 1Password account is
needed. Covers the paths that are otherwise only exercised by a manual local run:

* `secrets_fetch_enabled=false` plus the NUT_*_PASSWORD env vars: no `op` call at
  all, and the published facts come from the environment;
* env-override filtering: a ref covered by an env var is dropped from the stdin
  of the single `op inject` call, and the remaining refs resolve by name;
* the unresolved-reference guard: an `op` that hands references back verbatim
  makes the play fail loudly instead of publishing a literal `op://` string.

Run with: uv run pytest tests/ -k secrets
"""

import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.integration]

REPO_ROOT = Path(__file__).resolve().parent.parent
SECRETS_PLAYBOOK = REPO_ROOT / "playbooks" / "secrets.yml"

# The three secrets that have an environment-variable override in the playbook.
NUT_ENV_VARS = ("NUT_SECONDARY_PASSWORD", "NUT_HA_PASSWORD", "NUT_PRIMARY_PASSWORD")

# Wrapper playbook appended after the imported secrets play: it asserts that the
# facts published on localhost match the expectations passed via -e @<json>.
WRAPPER_PLAYBOOK_TEMPLATE = """---
- import_playbook: __SECRETS_PATH__

- name: Verify published secrets facts on localhost
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Assert published facts match the expectations
      ansible.builtin.assert:
        that:
          - (hostvars['localhost'] | default({}))[item.key] == item.value
        fail_msg: "published localhost fact '{{ item.key }}' does not match the expected value"
      loop: "{{ expected_facts | dict2items }}"

    - name: Assert facts that must stay unpublished are absent
      ansible.builtin.assert:
        that:
          - item not in (hostvars['localhost'] | default({}))
        fail_msg: "localhost fact '{{ item }}' must not have been published"
      loop: "{{ expected_absent | default([]) }}"
"""

# Stub `op` (run with the test's own interpreter via its shebang): records its
# stdin, then resolves every template-form reference on a line to a
# deterministic fake value derived from the 1Password item id.
STUB_OP_RESOLVING = r"""
import os
import re
import sys

if len(sys.argv) < 2 or sys.argv[1] != "inject":
    print(f"stub op: unexpected invocation: {' '.join(sys.argv[1:])}", file=sys.stderr)
    sys.exit(97)

stdin = sys.stdin.read()
with open(os.environ["OP_STUB_RECORD"], "w") as record:
    record.write(stdin)

lines = []
for line in stdin.splitlines():
    # {{ op://vault/<item-id>/<field> }}  ->  resolved-<item-id>
    # (fields may contain spaces, e.g. "public key")
    match = re.match(r"^\{\{[ ]*op://[^/\s]+/([^/\s]+)/.+ [ ]*}}$", line)
    lines.append(f"resolved-{match.group(1)}" if match else line)
sys.stdout.write("\n".join(lines) + "\n")
"""

# Stub `op`: hands stdin back verbatim, simulating an `op` version that leaves
# template-form references unresolved and still exits 0.
STUB_OP_PASSTHROUGH = """#!/bin/sh
cat
"""


def _require_ansible():
    if importlib.util.find_spec("ansible") is None:
        pytest.skip("ansible is not installed for the running interpreter; run via `uv run pytest`")


@pytest.fixture(autouse=True)
def _skip_without_ansible():
    _require_ansible()


@pytest.fixture(scope="module")
def secret_defs():
    """name -> op:// ref for every secret, parsed from playbooks/secrets.yml."""
    play = yaml.safe_load(SECRETS_PLAYBOOK.read_text())
    defs = play[0]["vars"]

    def refs_for(entry):
        return {d["name"]: d["op"] for d in entry}

    macos_refs = refs_for(defs["secrets_macos_admin_ref"])
    other_refs = refs_for(defs["secrets_op_refs"])
    # env var used for each overridable secret, e.g. NUT_SECONDARY_PASSWORD
    env_vars = {
        name: re.search(r"lookup\('ansible.builtin.env',\s*'([A-Z_]+)'\)", value).group(1)
        for name, value in defs["secrets_env_overrides"].items()
    }
    return {"macos": macos_refs, "other": other_refs, "env_vars": env_vars}


def _item_id(op_ref):
    """1Password item id from an op:// reference (not a secret, just the id)."""
    return re.search(r"op://[^/]+/([^/]+)/", op_ref).group(1)


def _make_stub_op(tmp_path, script, interpreter="/bin/sh"):
    """Install a stub `op` on PATH; it records its stdin to the returned path."""
    bin_dir = tmp_path / "stub_bin"
    bin_dir.mkdir(exist_ok=True)
    stub = bin_dir / "op"
    stub.write_text(f"#!{interpreter}\n{script}")
    stub.chmod(0o755)
    record = tmp_path / "op_inject_stdin.txt"
    return bin_dir, record


def _subprocess_env(tmp_path, nut_overrides=None, stub_bin=None):
    env = os.environ.copy()
    for var in NUT_ENV_VARS:
        env.pop(var, None)  # never inherit ambient NUT passwords into the run
    if nut_overrides:
        env.update(nut_overrides)
    if stub_bin is not None:
        env["PATH"] = f"{stub_bin}{os.pathsep}{env['PATH']}"
    return env


def _run_secrets_play(
    tmp_path,
    expected_facts,
    expected_absent=(),
    *,
    fetch_enabled=None,
    nut_overrides=None,
    stub_script=None,
    stub_interpreter="/bin/sh",
):
    """Run playbooks/secrets.yml plus a verification play asserting the facts."""
    wrapper = tmp_path / "verify_secrets.yml"
    wrapper.write_text(WRAPPER_PLAYBOOK_TEMPLATE.replace("__SECRETS_PATH__", str(SECRETS_PLAYBOOK)))
    inventory = tmp_path / "inventory.yml"
    inventory.write_text("all:\n  hosts:\n    localhost:\n      ansible_connection: local\n")
    expected = tmp_path / "expected.json"
    expected.write_text(json.dumps({"expected_facts": expected_facts, "expected_absent": list(expected_absent)}))

    cmd = [sys.executable, "-m", "ansible", "playbook", str(wrapper), "-i", str(inventory), "-e", f"@{expected}"]
    if fetch_enabled is not None:
        cmd += ["-e", f"secrets_fetch_enabled={'true' if fetch_enabled else 'false'}"]

    record = tmp_path / "op_inject_stdin.txt"
    if stub_script is not None:
        bin_dir, record = _make_stub_op(tmp_path, stub_script, interpreter=stub_interpreter)
        env = _subprocess_env(tmp_path, nut_overrides, stub_bin=bin_dir)
        env["OP_STUB_RECORD"] = str(record)
    else:
        env = _subprocess_env(tmp_path, nut_overrides)

    return subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=300), record


def test_fetch_disabled_publishes_env_nut_passwords(tmp_path):
    """With the fetch disabled and NUT_*_PASSWORD set, facts come from env and no
    op call happens (a real signed-in `op` on this machine would have failed it)."""
    overrides = {
        # Deliberately weak, non-secret fixtures for a test that never calls 1Password.
        "NUT_SECONDARY_PASSWORD": "env-secondary-password-1",  # pragma: allowlist secret
        "NUT_HA_PASSWORD": "env-ha-password-1",  # pragma: allowlist secret
        "NUT_PRIMARY_PASSWORD": "env-primary-password-1",  # pragma: allowlist secret
    }
    expected_facts = {
        # NUT passwords published from the environment...
        "secrets_nut_secondary_password": overrides["NUT_SECONDARY_PASSWORD"],
        "workstation_nut_secondary_password": overrides["NUT_SECONDARY_PASSWORD"],
        "secrets_nut_ha_password": overrides["NUT_HA_PASSWORD"],
        "secrets_nut_primary_password": overrides["NUT_PRIMARY_PASSWORD"],
        # ...while the 1Password-only secrets fall back to their empty default.
        "secrets_raspberry_pi_sudo": "",
        "secrets_raspberry_pi_authorized_keys": ["", ""],
    }
    result, _ = _run_secrets_play(
        tmp_path, expected_facts, ["ansible_become_password"], fetch_enabled=False, nut_overrides=overrides
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def test_env_override_drops_ref_from_single_op_call(tmp_path, secret_defs):
    """With the fetch enabled and NUT_SECONDARY_PASSWORD set, that ref is absent
    from the stdin of the (single) op inject call and its fact comes from env."""
    overrides = {"NUT_SECONDARY_PASSWORD": "env-secondary-password-1"}  # pragma: allowlist secret
    macos_admin_ref = secret_defs["macos"]["macos_admin_password"]
    controller_is_macos = platform.system() == "Darwin"

    expected_facts = {
        "secrets_nut_secondary_password": overrides["NUT_SECONDARY_PASSWORD"],
        "workstation_nut_secondary_password": overrides["NUT_SECONDARY_PASSWORD"],
        "secrets_nut_ha_password": f"resolved-{_item_id(secret_defs['other']['nut_ha_password'])}",
        "secrets_nut_primary_password": f"resolved-{_item_id(secret_defs['other']['nut_primary_password'])}",
        "secrets_raspberry_pi_sudo": f"resolved-{_item_id(secret_defs['other']['raspberry_pi_sudo'])}",
        "secrets_raspberry_pi_authorized_keys": [
            f"resolved-{_item_id(secret_defs['other']['giro_ssh_key'])}",
            f"resolved-{_item_id(secret_defs['other']['git_commit_ssh_key'])}",
        ],
    }
    expected_absent = [] if controller_is_macos else ["ansible_become_password"]
    if controller_is_macos:
        expected_facts["ansible_become_password"] = f"resolved-{_item_id(macos_admin_ref)}"

    result, record = _run_secrets_play(
        tmp_path,
        expected_facts,
        expected_absent,
        fetch_enabled=True,
        nut_overrides=overrides,
        stub_script=STUB_OP_RESOLVING,
        stub_interpreter=sys.executable,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    # Exactly one op call; every line is a template-form reference...
    stdin_lines = record.read_text().splitlines()
    covered_names = {name for name, var in secret_defs["env_vars"].items() if var in overrides}
    expected_lines = len(secret_defs["other"]) - len(covered_names) + (1 if controller_is_macos else 0)
    assert len(stdin_lines) == expected_lines
    assert all(re.fullmatch(r"\{\{ op://[^/\s]+/[^/\s]+/.+ \}\}", line) for line in stdin_lines), stdin_lines
    refs_in_stdin = {line[3:-3] for line in stdin_lines}  # strip the '{{ ' and ' }}' wrappers
    # ...the env-overridden one is dropped, the rest are all present.
    assert secret_defs["other"]["nut_secondary_password"] not in refs_in_stdin, refs_in_stdin
    for name in secret_defs["other"]:
        if name not in covered_names:
            assert secret_defs["other"][name] in refs_in_stdin, refs_in_stdin


def test_unresolved_op_refs_fail_loudly(tmp_path):
    """An op that leaves references unresolved must fail the play (unresolved
    refs contain 'op://'), instead of publishing them as passwords or keys."""
    result, _ = _run_secrets_play(tmp_path, {}, [], fetch_enabled=True, stub_script=STUB_OP_PASSTHROUGH)
    assert result.returncode != 0, f"play should fail on unresolved refs\nstdout:\n{result.stdout}"
    assert "Verify every secret was resolved" in result.stdout + result.stderr
