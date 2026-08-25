---
name: mac-workstation-update
description: Runs the Ansible playbook to update the local macOS workstation configuration.
---

1. Validates that the current system is macOS.
2. Executes the `site.yml` playbook using uv to ensure all local configurations, tools, and security settings are up to date.

### Prerequisites

- Run this skill from the repository root so relative paths such as `inventory/hosts.yml` and `site.yml` resolve correctly.
- You will be prompted for your sudo password when running the playbook because of the `--ask-become-pass` flag.
- Ensure `uv` is installed and the project dependencies needed for `ansible-playbook` are available.
- This skill is intended only for macOS.

// turbo
```bash
if [[ "$(uname)" != "Darwin" ]]; then
  echo "❌ This skill is intended only for macOS."
  exit 1
fi

echo "🚀 Updating local macOS workstation..."
uv run ansible-playbook -i inventory/hosts.yml site.yml --limit localhost --ask-become-pass
echo "✅ Workstation update complete."
```
