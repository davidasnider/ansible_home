# Project Overview

This is a personal development environment automation project that uses Ansible to configure and maintain consistent development setups across macOS and Linux systems. The project automates the installation and configuration of essential development tools, shell environments, and system settings.

## Purpose
- Automate fresh system setup for development environments
- Maintain consistent configurations across multiple machines
- Reduce manual setup time when switching between systems
- Provide reproducible development environment provisioning

## Key Technologies
- **Ansible**: Infrastructure as code for configuration management (Ansible 13+)
- **Python 3.12+**: Runtime environment with uv for dependency management
- **Zsh + Oh My Zsh**: Enhanced shell experience with "Pro-Lazy" initialization
- **1Password CLI**: Secure secrets and environment variable management
- **oh-my-posh**: Cross-platform prompt theming engine (with Nerd Fonts)

## Supported Platforms
- macOS (using Homebrew for package management)
- Linux (using apt package manager, tested on Ubuntu/Debian)

# Architecture & Directory Structure

## Project Layout

```
ansible_home/
├── Makefile                    # macOS development setup automation
├── bootstrap.sh               # Linux bootstrap script
├── site.yml                   # Master execution playbook
├── scripts/
│   └── check_updates.py       # Update checker script
├── pyproject.toml             # Python project configuration and dependencies
├── uv.lock                # Locked dependency versions
├── inventory/
│   └── hosts.yml              # Ansible inventory structure
├── playbooks/
│   ├── workstations.yml       # Workstation playbook with OS detection
│   └── raspberry_pis.yml      # Raspberry Pi execution playbook
├── roles/
│   ├── docker/                # Docker installation role
│   ├── home_assistant_remote/ # Home Assistant remote node configuration
│   ├── raspberry_pi/          # Raspberry Pi baseline configuration
│   └── workstation/            # Core workstation configuration role
│       ├── handlers/
│       │   └── main.yml        # Event handlers
│       └── tasks/
│           ├── main.yml        # Role entry point (OS detection)
│           ├── local-linux.yml # Linux-specific tasks
│           ├── local-mac.yml   # macOS-specific tasks
│           ├── zshrc-linux     # Linux zsh configuration template
├── src/
│   └── steel_mountain_ansible/    # Python package structure
└── tests/                     # Test files
```

## Architecture Principles

### Role-Based Organization
- **Single Role**: The `localhost` role contains all local machine configuration tasks
- **Platform Separation**: OS-specific tasks are separated into different files
- **Task Organization**: Related tasks are grouped logically within each platform file

### OS Detection Pattern (Standard Role Architecture)
The `workstation` role uses a standard `tasks/main.yml` entry point to detect the operating system and delegate to platform-specific logic:
- `ansible_facts['system'] == 'Darwin'` → includes `local-mac.yml`
- `ansible_facts['system'] == 'Linux'` → includes `local-linux.yml`

### Configuration Management
- **Templates**: Shell configuration files (like `zshrc-linux`) are stored as templates
- **Variables**: Environment-specific variables are managed through Ansible facts and environment lookups
- **Idempotency**: All tasks are designed to be safely run multiple times

# Development Environment Setup

## Prerequisites

### macOS
- Xcode Command Line Tools (will be prompted during first run)
- Internet connection for Homebrew installation

### Linux (Ubuntu/Debian)
- `sudo` access for package installation
- Internet connection for package downloads

## Quick Start

### macOS Setup
```bash
git clone https://github.com/davidasnider/ansible_home.git
cd ansible_home
make dev-setup
source .venv/bin/activate
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml
```

### Linux Setup
```bash
git clone https://github.com/davidasnider/ansible_home.git
cd ansible_home
./bootstrap.sh
```

### Raspberry Pi Setup
```bash
git clone https://github.com/davidasnider/ansible_home.git
cd ansible_home
# Ensure you have your IPs configured in inventory/hosts.yml
uv sync
uv run ansible-playbook -i inventory/hosts.yml --limit raspberry_pis site.yml
```

## Detailed Setup Process

### macOS (`make dev-setup`)
1. **Homebrew Installation**: Installs Homebrew if not present
2. **Python 3.11+**: Ensures compatible Python version via Homebrew
3. **uv Installation**: Installs uv for dependency management
4. **Virtual Environment**: Creates `.venv` directory and installs dependencies

### Linux (`bootstrap.sh`)
1. **System Update**: Updates package cache and upgrades existing packages
2. **Dependencies**: Installs `python3-venv` and `uv`
3. **Virtual Environment**: Creates `.venv` and activates it
4. **uv Install**: Installs project dependencies
5. **Sudo Password**: Prompts for sudo password and runs the main playbook

## Python Environment Management

### uv Configuration
- **Package Mode**: Disabled (`package-mode = false`) as this is a configuration project
- **Dependencies**: Ansible 11.5+ and hvac for Vault integration
- **Dev Dependencies**: pre-commit for code quality

### Virtual Environment
- **Location**: `.venv/` in project root
- **Activation**: `source .venv/bin/activate` (manual) or automatic via uv
- **Isolation**: Ensures consistent Ansible and Python versions across runs

# Ansible Playbook Structure

The entry point playbook uses the standard `roles` keyword to apply the workstation configuration:

```yaml
- name: Setup Workstations
  hosts: workstations
  gather_facts: true
  roles:
    - workstation
```

## Scalable Design Patterns

### OS Detection Strategy
- **Fact-Based Routing**: Uses `ansible_system` and `ansible_os_family` facts for OS detection
- **Extensible Conditions**: Pattern supports adding Windows (`ansible_system == 'Win32NT'`), FreeBSD, etc.
- **Distribution-Specific**: Can differentiate between Ubuntu/CentOS/RHEL using `ansible_distribution`

### Current Inventory (`inventory/hosts.yml`)
```yaml
all:
  children:
    workstations:
      children:
        local_workstations:
          hosts:
            localhost:
              ansible_connection: local
              ansible_python_interpreter: /usr/bin/python3
        networked_workstations:
          hosts:
            # workstation1:
            #   ansible_host: 192.168.1.50
    raspberry_pis:
      hosts:
        # pi1:
        #   ansible_host: 192.168.1.100
        #   ansible_user: pi
```

### Future Remote Host Support
The current framework structure will extend to support:
- **Multiple Host Groups**: Different inventory groups for workstations, servers, IoT devices
- **OS-Specific Roles**: Dedicated roles for Windows, various Linux distributions, macOS
- **Environment-Specific Playbooks**: Separate playbooks for development, staging, production

## Role Architecture for Multi-OS Support

### Current Structure
- **localhost Role**: Contains local development environment setup
- **OS-Specific Tasks**: Separated by platform within single role

### Planned Evolution
- **OS-Specific Roles**: `roles/macos/`, `roles/ubuntu/`, `roles/windows/`
- **Function-Specific Roles**: `roles/web-server/`, `roles/database/`, `roles/monitoring/`
- **Shared Components**: `roles/common/` for cross-platform tasks

# Platform-Specific Configurations

## macOS Configuration (`roles/workstation/tasks/local-mac.yml`)

### Package Management
- **Homebrew**: Primary package manager with automatic installation
- **Formulae**: Command-line tools (gh, htop, macmon, oh-my-posh, uv, pre-commit, pulumi, opencode, imsg, pi-coding-agent, zsh-autocomplete, zsh-autosuggestions, zsh-history-substring-search, zsh-syntax-highlighting)
- **Casks**: GUI applications, command-line utilities, and fonts (1Password, 1Password CLI, Antigravity CLI, iTerm2, VS Code, OrbStack, Rectangle, Obsidian, font-meslo-lg-nerd-font)
- **Update Strategy**: Checks last update time, only updates if >24 hours old

### Key Features
- **Oh My Zsh**: Automated installation with custom plugin configuration
- **Shell Customization**: Comprehensive zsh configuration with syntax highlighting and autocomplete

### macOS-Specific Tools
```yaml
# Homebrew packages
- gh
- htop
- macmon
- oh-my-posh
- uv
- pre-commit
- pulumi
- opencode
- imsg
- zsh-autocomplete
- zsh-autosuggestions
- zsh-syntax-highlighting
- zsh-history-substring-search
- pi-coding-agent
# Homebrew casks
- 1password
- 1password-cli
- antigravity-cli
- iterm2
- visual-studio-code
- orbstack
- rectangle
- obsidian
- font-meslo-lg-nerd-font

# Custom scripts/binaries
- pulumi
- opencode
- hermes-agent
```

## Linux Configuration (`roles/workstation/tasks/local-linux.yml`)

### Package Management
- **APT**: Uses apt package manager for Ubuntu/Debian systems
- **Cache Management**: Updates cache with 24-hour validity period
- **System Integration**: Sets zsh as default shell system-wide

### Key Features
- **1Password CLI**: Complete setup including GPG key management and repository addition
- **oh-my-posh**: Manual installation to `~/.local/bin` via curl script
- **Shell Configuration**: Uses template file (`zshrc-linux`) for consistent setup

### Linux-Specific Packages
```yaml
# APT packages
- gh
- htop
- jq
- uv
- pre-commit
- zsh
- zsh-autosuggestions
- zsh-syntax-highlighting
- unzip
- 1password-cli (via custom repository)

# Custom scripts/binaries
- oh-my-posh
- opencode
- pulumi
```

## Platform Differences

### Global Features
- **Gemini Agent Integration**: Automatically links local agent workflows (`~/.agents/workflows`) to the Gemini configuration directory (`~/.gemini/agents`) if both directories are present on the system.

### Package Managers
- **macOS**: Homebrew formulae and casks
- **Linux**: APT packages with custom repositories for specialized tools

### Shell Setup Strategy
- **macOS**: Dynamic configuration block in existing `.zshrc`
- **Linux**: Complete `.zshrc` replacement using template file

### Path Management
- **macOS**: Homebrew paths (`/opt/homebrew/`)
- **Linux**: System paths (`/usr/share/`, `~/.local/bin`)

### Authentication & Security
- **macOS**: 1Password app + CLI via Homebrew cask
- **Linux**: 1Password CLI-only with manual GPG key and repository setup

## Common Tasks Across Platforms
- Git user configuration (name and email)
- `~/code` directory creation
- Oh My Zsh installation and configuration (extracted to `roles/workstation/tasks/install-oh-my-zsh.yml`)
- Zsh plugin management (syntax highlighting, autosuggestions)
- oh-my-posh theme engine setup
- Python virtual environment detection and auto-activation

# Security & Secrets Management

## Current Implementation

### 1Password Integration
The project uses 1Password CLI for secure secrets management with a streamlined workflow:

```bash
# Login and load environment variables in one command
alias opload='eval "$(op signin)" && eval "$(cat ~/.env | op inject)"'
```

### Environment Variables
Required secrets are managed through a `~/.env` file with 1Password secret references:

```bash
# Example .env file structure
export GITHUB_TOKEN="op://vault/github-token/token"
export ANSIBLE_SUDO_PASS="op://vault/sudo-password/password"
```

### Validation System
The zsh configuration checks for the presence of the .env file and verifies 1Password authentication:

```bash
# Warns user if .env file is missing and provides instructions to create it
# Checks if 1Password CLI is authenticated, and if not, prompts to use opload
```

## Security Features

### Sudo Password Management
- **Environment Variable**: Uses `ANSIBLE_SUDO_PASS` for automated privilege escalation
- **Secure Storage**: Password stored in 1Password, referenced via secret URI
- **Bootstrap Integration**: `bootstrap.sh` prompts for password when needed

### Secret Storage Strategy
- **No Hardcoded Secrets**: All sensitive data referenced via 1Password URIs
- **User-Specific Paths**: Uses `{{ lookup('env', 'HOME') }}` for user directory access
- **Environment Isolation**: Secrets loaded per-session via `opload` alias

### Platform-Specific Security
- **macOS**: 1Password app provides GUI and CLI integration
- **Linux**: 1Password CLI-only with GPG key verification during installation

## Planned Enhancements (from TODO.md)

### HashiCorp Vault Integration
- **Centralized Management**: Planned integration for multi-host secret management
- **hvac Dependency**: Already included in `pyproject.toml` for Vault API access
- **Fallback Strategy**: Ansible Vault as backup for local encryption

### Future Architecture
```yaml
# Planned Vault integration pattern
vars:
  vault_token: "{{ lookup('env', 'VAULT_TOKEN') }}"
  database_password: "{{ lookup('hashivault', 'secret/data/database', 'password') }}"
```

## Best Practices

### Secret Rotation
- 1Password provides built-in secret rotation capabilities
- Environment variables automatically updated when secrets change in vault
- No code changes required for credential updates

### Access Control
- **Principle of Least Privilege**: Each system accesses only required secrets
- **Audit Trail**: 1Password maintains access logs and usage history
- **Session Management**: Secrets loaded per-session, not persisted globally

### Development vs Production
- **Development**: Local 1Password CLI with user vaults
- **Production**: Planned HashiCorp Vault with centralized management
- **Consistent Interface**: Environment variable pattern works across both systems

# Common Tasks & Workflows

## Daily Operations

### Running the Main Playbook
```bash
# Full setup (first time or complete refresh)
source .venv/bin/activate
ansible-playbook -i inventory/hosts.yml site.yml

# Quick setup with bootstrap (Linux)
./bootstrap.sh
```

### Loading Secrets
```bash
# Load environment variables from 1Password
opload

# Verify required variables are loaded
echo $GITHUB_TOKEN
echo $ANSIBLE_SUDO_PASS
```

### GitHub Token Requirement
The `GITHUB_TOKEN` environment variable is required for certain infrastructure automation scripts (e.g., in `infrastructure/__main__.py`). Ensure it is loaded into your environment. Tests verify that an error is correctly raised if it is missing, using fully isolated subprocess environments.

## Development Workflows

### Adding New Packages

#### macOS (Homebrew)
```yaml
# Add to roles/workstation/tasks/local-mac.yml
- name: Update Homebrew and install packages
  community.general.homebrew:
    name:
      - existing-package
      - new-package-name  # Add here
    state: present
    update_homebrew: "{{ update_brew }}"
```

#### Linux (APT)
```yaml
# Add to roles/workstation/tasks/local-linux.yml
- name: Install packages
  ansible.builtin.apt:
    name:
      - existing-package
      - new-package-name  # Add here
    state: present
    update_cache: yes
```

### Modifying Shell Configuration

#### Update Zsh Plugins (Linux)
Edit `roles/workstation/tasks/zshrc-linux` template:
```bash
# Add new plugin to the plugins array
plugins=(git gh pip python systemd new-plugin)
```

#### Update Zsh Configuration (macOS)
Modify the `ansible.builtin.blockinfile` task in `local-mac.yml`:
```yaml
block: |
  # Add new configuration here
  source /opt/homebrew/share/new-plugin/new-plugin.zsh
```

### Testing Changes

#### Syntax Validation
The project uses automated syntax validation for all playbooks. This is the fastest way to ensure your changes are valid Ansible code.
```bash
# Run all syntax checks via Makefile
make test-syntax

# Or check a specific playbook manually
ansible-playbook --syntax-check -i inventory/hosts.yml playbooks/workstations.yml
```

#### Linting
We use `ansible-lint` to enforce best practices and security rules.
```bash
# Run lint checks via Makefile
make test-lint

# Or run manually
ansible-lint roles/
```

#### Dry Run (Mocked)
Before applying changes to a live system, perform a dry run to see exactly what Ansible will do.
```bash
# Perform a dry run on the workstation playbook
ansible-playbook --check --diff -i inventory/hosts.yml playbooks/workstations.yml
```

## Maintenance Workflows

### Updating Dependencies
```bash
# Update uv dependencies
uv lock --upgrade

# Update Homebrew packages (macOS)
brew update && brew upgrade

# Update APT packages (Linux)
sudo apt update && sudo apt upgrade
```

### Environment Refresh
```bash
# Clean and rebuild Python environment
rm -rf .venv
uv sync

# Or use make target (macOS)
make dev-setup
```

### Checking Application Updates
```bash
# Check for updates to remote node applications (e.g., `remote_homeassistant` and `home-assistant/core`)
make check-updates
```

### Secret Rotation
```bash
# Update secrets in 1Password
op item edit "item-name" password="new-password"

# Reload environment variables
opload
```

## Git Workflows

### Making Changes
```bash
# Create feature branch
git checkout -b feature/add-new-tool

# Make changes to playbooks/roles
# Test changes locally
ansible-playbook --check -i inventory/hosts.yml playbooks/workstations.yml

# Commit changes
git add .
git commit -m "feat: add new development tool"

# Push and create PR using gh CLI
git push origin feature/add-new-tool
gh pr create --title "Add new development tool" --body "Description of changes"

# Or create draft PR for work in progress
gh pr create --draft --title "WIP: Add new development tool"
```

### Applying Updates
```bash
# Pull latest changes
git checkout main
git pull origin main

# Apply updated configuration
source .venv/bin/activate
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml
```

### PR Management
```bash
# View open PRs
gh pr list

# Check PR status
gh pr status

# Merge PR after approval
gh pr merge --squash

# Clean up local branch after merge using the automated target
make cleanup
```

## Repository Maintenance

The repository includes automated tools for keeping your local environment clean and consistent.

### The `make cleanup` utility
After you have merged a Pull Request, you can run `make cleanup` to:
1.  Switch back to the `main` branch.
2.  Pull the latest changes from the remote.
3.  Prune remote tracking branches.
4.  Safely delete any local branches that have been merged.
5.  Synchronize project dependencies using `uv sync`.

# Troubleshooting Guide

## Common Issues

### Environment Setup Problems

#### uv Installation Fails
```bash
# macOS: Ensure Homebrew is properly installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Linux: Install via system package manager
sudo apt update && sudo apt install uv
```

#### Python Virtual Environment Issues
```bash
# Remove corrupted virtual environment
rm -rf .venv
rm -rf .venv

# Recreate environment
python3 -m venv .venv
uv sync
```

### Ansible Execution Problems

#### Sudo Password Issues
```bash
# Ensure ANSIBLE_SUDO_PASS is set
echo $ANSIBLE_SUDO_PASS

# Load secrets if missing
opload

# Alternative: Set manually for testing
export ANSIBLE_SUDO_PASS="your-sudo-pass"  # pragma: allowlist secret
```

#### Permission Denied Errors
```bash
# Check file permissions
ls -la ~/.ssh/
ls -la ~/.zshrc

# Fix common permission issues
chmod 600 ~/.ssh/config
chmod 644 ~/.zshrc
```

#### Package Installation Failures
```bash
# macOS: Update Homebrew
brew update
brew doctor

# Linux: Update package cache
sudo apt update
sudo apt --fix-broken install
```

### Shell Configuration Issues

#### Zsh Not Default Shell
```bash
# Check current shell
echo $SHELL

# Set zsh as default (manual)
chsh -s $(which zsh)

# Re-run Ansible task
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml --tags shell
```

#### Oh My Zsh Installation Problems
```bash
# Remove existing installation
rm -rf ~/.oh-my-zsh

# Clear zsh configuration
mv ~/.zshrc ~/.zshrc.backup

# Re-run playbook
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml
```

#### Plugin Loading Errors
```bash
# Check plugin paths (Linux)
ls -la /usr/share/zsh-*

# Check plugin paths (macOS)
ls -la /opt/homebrew/share/zsh-*

# Verify plugin sources in .zshrc
grep -n "source.*zsh" ~/.zshrc
```

## Platform-Specific Issues

### macOS Gotchas

#### Xcode Command Line Tools
```bash
# Install if prompted
xcode-select --install

# Verify installation
xcode-select -p
```

#### Homebrew Path Issues
```bash
# Add Homebrew to PATH
eval "$(/opt/homebrew/bin/brew shellenv)"

# Add to shell profile permanently
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

### Linux Gotchas

#### WSL-Specific Issues
```bash
# Fix systemd issues in WSL
sudo systemctl status

# Alternative package installation without systemd
sudo apt install --no-install-recommends package-name
```

#### 1Password GPG Key Issues
```bash
# Re-download and import GPG key
wget -O- https://downloads.1password.com/linux/keys/1password.asc | sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg

# Verify keyring
ls -la /usr/share/keyrings/1password-archive-keyring.gpg
```

## Debugging Techniques

### Ansible Debugging
```bash
# Verbose output
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml -v

# Very verbose (includes task details)
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml -vv

# Extremely verbose (includes connection debugging)
ansible-playbook -i inventory/hosts.yml playbooks/workstations.yml -vvv
```

### Dry Run Testing
```bash
# Check what would change without applying
ansible-playbook --check -i inventory/hosts.yml playbooks/workstations.yml

# Check specific tasks
ansible-playbook --check --start-at-task "Install packages" -i inventory/hosts.yml playbooks/workstations.yml
```

### Manual Task Testing
```bash
# Test individual commands
which zsh
python3 --version
uv --version

# Test 1Password CLI
op whoami
op vault list
```

## Getting Help

### Log Files
- Ansible logs: Use `-vvv` flag for detailed output
- System logs: `journalctl -f` (Linux) or `Console.app` (macOS)
- Shell startup: Add `set -x` to `.zshrc` for debugging

### Useful Commands
```bash
# System information
ansible localhost -m setup

# Test connectivity
ansible localhost -m ping

# List installed packages
brew list (macOS) or dpkg -l (Linux)
```
