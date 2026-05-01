---
name: mac-workstation-update
description: Runs the Ansible playbook to update the local macOS workstation configuration.
---

1. Validates that the current system is macOS.
2. Executes the `workstations.yml` playbook using uv to ensure all local configurations, tools, and security settings are up to date.

### Prerequisites

- Run this skill from the repository root so relative paths such as `inventory/hosts.yml` and `playbooks/workstations.yml` resolve correctly.
- Export `ANSIBLE_SUDO_PASS` in your environment before running this skill; the playbook reads it for `ansible_become_pass`.
- Ensure `uv` is installed and the project dependencies needed for `ansible-playbook` are available.
- This skill is intended only for macOS.

// turbo
```bash
if [[ "$(uname)" != "Darwin" ]]; then
  echo "❌ This skill is intended only for macOS."
  exit 1
fi

echo "🚀 Updating local macOS workstation..."
uv run ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml --limit localhost
echo "✅ Workstation update complete."
```
