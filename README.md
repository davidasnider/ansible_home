# Project Overview

This is a personal development environment automation project that uses Ansible to configure and maintain consistent development setups across macOS and Linux systems. The project automates the installation and configuration of essential development tools, shell environments, and system settings.

## Purpose
- Automate fresh system setup for development environments
- Maintain consistent configurations across multiple machines
- Reduce manual setup time when switching between systems
- Provide reproducible development environment provisioning

## Key Technologies
- **Ansible**: Infrastructure as code for configuration management
- **Python 3.11+**: Runtime environment with Poetry for dependency management
- **Zsh + Oh My Zsh**: Enhanced shell experience with plugins and themes
- **1Password CLI**: Secure secrets and environment variable management
- **oh-my-posh**: Cross-platform prompt theming engine

## Supported Platforms
- macOS (using Homebrew for package management)
- Linux (using apt package manager, tested on Ubuntu/Debian)

# Architecture & Directory Structure

## Project Layout

```
ansible_home/
├── Makefile                    # macOS development setup automation
├── bootstrap.sh               # Linux bootstrap script
├── pyproject.toml             # Python project configuration and dependencies
├── poetry.lock                # Locked dependency versions
├── inventory/
│   └── local.yml              # Ansible inventory for localhost
├── playbooks/
│   └── local-main.yml         # Main playbook with OS detection
├── roles/
│   └── localhost/
│       ├── handlers/
│       │   └── main.yml       # Event handlers (if needed)
│       └── tasks/
│           ├── local-linux.yml    # Linux-specific tasks
│           ├── local-mac.yml      # macOS-specific tasks
│           └── zshrc-linux        # Linux zsh configuration template
├── src/
│   └── steel_mountain_ansible/    # Python package structure
└── tests/                     # Test files
```

## Architecture Principles

### Role-Based Organization
- **Single Role**: The `localhost` role contains all local machine configuration tasks
- **Platform Separation**: OS-specific tasks are separated into different files
- **Task Organization**: Related tasks are grouped logically within each platform file

### OS Detection Pattern
The main playbook (`local-main.yml`) uses Ansible's `gather_facts` to detect the operating system and conditionally include the appropriate task file:
- `ansible_system == 'Darwin'` → includes `local-mac.yml`
- `ansible_system == 'Linux'` → includes `local-linux.yml`

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
ansible-playbook -i inventory/local.yml playbooks/local-main.yml
```

### Linux Setup
```bash
git clone https://github.com/davidasnider/ansible_home.git
cd ansible_home
./bootstrap.sh
```

## Detailed Setup Process

### macOS (`make dev-setup`)
1. **Homebrew Installation**: Installs Homebrew if not present
2. **Python 3.11+**: Ensures compatible Python version via Homebrew
3. **Poetry Installation**: Installs Poetry for dependency management
4. **Virtual Environment**: Creates `.venv` directory and installs dependencies

### Linux (`bootstrap.sh`)
1. **System Update**: Updates package cache and upgrades existing packages
2. **Dependencies**: Installs `python3-venv` and `python3-poetry`
3. **Virtual Environment**: Creates `.venv` and activates it
4. **Poetry Install**: Installs project dependencies
5. **Sudo Password**: Prompts for sudo password and runs the main playbook

## Python Environment Management

### Poetry Configuration
- **Package Mode**: Disabled (`package-mode = false`) as this is a configuration project
- **Dependencies**: Ansible 11.5+ and hvac for Vault integration
- **Dev Dependencies**: pre-commit for code quality

### Virtual Environment
- **Location**: `.venv/` in project root
- **Activation**: `source .venv/bin/activate` (manual) or automatic via poetry
- **Isolation**: Ensures consistent Ansible and Python versions across runs

# Ansible Playbook Structure

## Main Playbook (`playbooks/local-main.yml`)

The current entry point playbook is designed for localhost setup but follows patterns that scale to remote hosts:

```yaml
- name: Detect OS and include the appropriate local task file
  hosts: localhost
  gather_facts: true
  vars:
    ansible_become_pass: "{{ lookup('ansible.builtin.env', 'ANSIBLE_SUDO_PASS') }}"
  tasks:
    - name: Include local-mac tasks if MacOS
      ansible.builtin.include_tasks: ../roles/localhost/tasks/local-mac.yml
      when: ansible_system == 'Darwin'
    - name: Include local-linux tasks if Linux
      ansible.builtin.include_tasks: ../roles/localhost/tasks/local-linux.yml
      when: ansible_system == 'Linux'
```

## Scalable Design Patterns

### OS Detection Strategy
- **Fact-Based Routing**: Uses `ansible_system` and `ansible_os_family` facts for OS detection
- **Extensible Conditions**: Pattern supports adding Windows (`ansible_system == 'Win32NT'`), FreeBSD, etc.
- **Distribution-Specific**: Can differentiate between Ubuntu/CentOS/RHEL using `ansible_distribution`

### Future Remote Host Support
The current localhost-focused structure will extend to support:
- **Multiple Host Groups**: Different inventory groups for workstations, servers, IoT devices
- **OS-Specific Roles**: Dedicated roles for Windows, various Linux distributions, macOS
- **Environment-Specific Playbooks**: Separate playbooks for development, staging, production

### Variable Management
- **Environment Lookup**: Currently uses local environment variables
- **Future Vault Integration**: Will support HashiCorp Vault for remote host secrets
- **Host-Specific Variables**: Pattern supports `host_vars/` and `group_vars/` directories

### Current Inventory (`inventory/local.yml`)
```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: /usr/bin/python3
```

**Future Inventory Structure** (example):
```yaml
all:
  children:
    workstations:
      hosts:
        laptop-mac:
          ansible_host: 192.168.1.100
          ansible_system: Darwin
        desktop-linux:
          ansible_host: 192.168.1.101
          ansible_system: Linux
    servers:
      hosts:
        web-server:
          ansible_host: 10.0.1.10
          ansible_system: Linux
          ansible_distribution: Ubuntu
```

## Role Architecture for Multi-OS Support

### Current Structure
- **localhost Role**: Contains local development environment setup
- **OS-Specific Tasks**: Separated by platform within single role

### Planned Evolution
- **OS-Specific Roles**: `roles/macos/`, `roles/ubuntu/`, `roles/windows/`
- **Function-Specific Roles**: `roles/web-server/`, `roles/database/`, `roles/monitoring/`
- **Shared Components**: `roles/common/` for cross-platform tasks

# Platform-Specific Configurations

## macOS Configuration (`roles/localhost/tasks/local-mac.yml`)

### Package Management
- **Homebrew**: Primary package manager with automatic installation
- **Formulae**: Command-line tools (gh, htop, oh-my-posh, poetry, pre-commit)
- **Casks**: GUI applications (1Password, 1Password CLI, iTerm2, VS Code)
- **Update Strategy**: Checks last update time, only updates if >24 hours old

### Key Features
- **Dotfiles Integration**: Clones and manages dotfiles repository from GitHub
- **Oh My Zsh**: Automated installation with custom plugin configuration
- **Shell Customization**: Comprehensive zsh configuration with syntax highlighting and autocomplete

### macOS-Specific Tools
```yaml
# Homebrew packages
- gh, htop, oh-my-posh, poetry, pre-commit
- zsh-autocomplete, zsh-autosuggestions, zsh-fast-syntax-highlighting

# Homebrew casks
- 1password, 1password-cli, iterm2, visual-studio-code
```

## Linux Configuration (`roles/localhost/tasks/local-linux.yml`)

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
- gh, htop, jq, python3-poetry, pre-commit, zsh
- zsh-autosuggestions, zsh-syntax-highlighting, unzip
- 1password-cli (via custom repository)
```

## Platform Differences

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
- Oh My Zsh installation and configuration
- Zsh plugin management (syntax highlighting, autosuggestions)
- oh-my-posh theme engine setup
- Python virtual environment detection and auto-activation

# Security & Secrets Management

## Current Implementation

### 1Password Integration
The project uses 1Password CLI for secure secrets management with a streamlined workflow:

```bash
# Login and load environment variables in one command
alias opload='eval $(op signin) && eval $(cat ~/.env | op inject --)'
```

### Environment Variables
Required secrets are managed through a `~/.env` file with 1Password secret references:

```bash
# Example .env file structure
export GITHUB_TOKEN="op://vault/github-token/token"
export ANSIBLE_SUDO_PASS="op://vault/sudo-password/password"
```

### Validation System
The zsh configuration includes automatic validation of required environment variables:

```bash
# Required variables checked at shell startup
REQUIRED_VARS=(GITHUB_TOKEN ANSIBLE_SUDO_PASS)

# Warns user if variables are missing from .env file
# Provides instructions for creating missing entries
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
ansible-playbook -i inventory/local.yml playbooks/local-main.yml

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

## Development Workflows

### Adding New Packages

#### macOS (Homebrew)
```yaml
# Add to roles/localhost/tasks/local-mac.yml
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
# Add to roles/localhost/tasks/local-linux.yml
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
Edit `roles/localhost/tasks/zshrc-linux` template:
```bash
# Add new plugin to the plugins array
plugins=(git gh pip poetry python systemd new-plugin)
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
```bash
# Check playbook syntax
ansible-playbook --syntax-check -i inventory/local.yml playbooks/local-main.yml

# Dry run to see what would change
ansible-playbook --check -i inventory/local.yml playbooks/local-main.yml
```

#### Targeted Testing
```bash
# Run specific tasks using tags (when implemented)
ansible-playbook -i inventory/local.yml playbooks/local-main.yml --tags "shell,packages"

# Test on specific host groups
ansible-playbook -i inventory/production.yml playbooks/local-main.yml --limit "workstations"
```

## Maintenance Workflows

### Updating Dependencies
```bash
# Update Poetry dependencies
poetry update

# Update Homebrew packages (macOS)
brew update && brew upgrade

# Update APT packages (Linux)
sudo apt update && sudo apt upgrade
```

### Environment Refresh
```bash
# Clean and rebuild Python environment
poetry env remove --all
poetry install

# Or use make target (macOS)
make dev-setup
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
ansible-playbook --check -i inventory/local.yml playbooks/local-main.yml

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
ansible-playbook -i inventory/local.yml playbooks/local-main.yml
```

### PR Management
```bash
# View open PRs
gh pr list

# Check PR status
gh pr status

# Merge PR after approval
gh pr merge --squash

# Clean up local branch after merge
git checkout main
git pull origin main
git branch -d feature/add-new-tool
```

# Troubleshooting Guide

## Common Issues

### Environment Setup Problems

#### Poetry Installation Fails
```bash
# macOS: Ensure Homebrew is properly installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

# Linux: Install via system package manager
sudo apt update && sudo apt install python3-poetry
```

#### Python Virtual Environment Issues
```bash
# Remove corrupted virtual environment
poetry env remove --all
rm -rf .venv

# Recreate environment
python3 -m venv .venv
poetry install
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
ansible-playbook -i inventory/local.yml playbooks/local-main.yml --tags shell
```

#### Oh My Zsh Installation Problems
```bash
# Remove existing installation
rm -rf ~/.oh-my-zsh

# Clear zsh configuration
mv ~/.zshrc ~/.zshrc.backup

# Re-run playbook
ansible-playbook -i inventory/local.yml playbooks/local-main.yml
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
ansible-playbook -i inventory/local.yml playbooks/local-main.yml -v

# Very verbose (includes task details)
ansible-playbook -i inventory/local.yml playbooks/local-main.yml -vv

# Extremely verbose (includes connection debugging)
ansible-playbook -i inventory/local.yml playbooks/local-main.yml -vvv
```

### Dry Run Testing
```bash
# Check what would change without applying
ansible-playbook --check -i inventory/local.yml playbooks/local-main.yml

# Check specific tasks
ansible-playbook --check --start-at-task "Install packages" -i inventory/local.yml playbooks/local-main.yml
```

### Manual Task Testing
```bash
# Test individual commands
which zsh
python3 --version
poetry --version

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
