---
name: mac-workstation-update
description: Runs the Ansible playbook to update the local macOS workstation configuration.
---

1. Validates that the current system is macOS.
2. Executes the `workstations.yml` playbook using Poetry to ensure all local configurations, tools, and security settings are up to date.

// turbo
```bash
if [[ "$(uname)" != "Darwin" ]]; then
  echo "❌ This skill is intended only for macOS."
  exit 1
fi

echo "🚀 Updating local macOS workstation..."
poetry run ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml --limit localhost
echo "✅ Workstation update complete."
```
