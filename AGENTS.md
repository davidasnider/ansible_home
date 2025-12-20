# AI Agent Instructions for ansible_home

This document provides guidelines and instructions for AI agents to effectively contribute to this project.

## 1. Project Overview

This is an Ansible project that automates the setup and configuration of a local development environment on macOS and Linux. The goal is to use Ansible to install software, manage system settings, and enforce security best practices in a consistent and reproducible way.

## 2. Core Principles

When making changes to this repository, please adhere to the following principles:

- **Ansible is Authoritative**: Never make system changes or copy files manually. All changes to the environment configuration must be done through Ansible playbooks and roles.
- **Use the Makefile**: The `Makefile` contains all necessary commands for setup, testing, and validation. Use `make` targets instead of running commands manually.
- **Dependencies are Managed**: All Python dependencies are managed with Poetry and are defined in `pyproject.toml`. Do not use `pip` directly.
- **Validate Before Committing**: Always run the relevant tests to ensure your changes are correct and do not break existing functionality before creating a pull request.
- **Sign Your Commits**: All commits must be GPG signed. A pre-commit hook is in place to enforce this.

## 3. Environment Setup

To set up the local development environment for the first time, run the following command:

```bash
make dev-setup
```
This will install all necessary tools and project dependencies into a local `.venv` directory.

## 4. Testing & Validation

Use the following `make` targets to test and validate your changes. The `Makefile` is the single source of truth for all testing commands.

| Command                               | Description                                                                                                                              | When to Use                                      |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `make test-lint`                      | Runs all pre-commit hooks for formatting and static analysis, including `ansible-lint`.                                                  | Frequently, for fast feedback while coding.      |
| `make test`                           | Runs the main test suite, including linting and all core Molecule scenarios.                                                             | Before creating a pull request.                  |
| `make test-fast`                      | Runs an optimized, parallelized version of the test suite for quicker local validation.                                                  | For quick checks during development.             |
| `make test-all`                       | Runs the complete test suite, including code coverage analysis.                                                                          | Before finalizing major features.                |
| `make molecule-test-scenario SCENARIO=<name>` | Runs a specific Molecule test scenario (e.g., `default`, `linux`, `idempotence`, `macos`). | For targeted testing of a specific environment.  |

## 5. Agent-Specific Configuration

### GitHub MCP Setup (for Claude)
To enable GitHub integration with the Claude agent, you may need to set up the GitHub MCP server:

1.  First, export your GitHub Personal Access Token:
    ```zsh
    export GITHUB_TOKEN=<your-PAT>
    ```

2.  Add the GitHub MCP server to Claude:
    ```zsh
    claude mcp add github https://api.githubcopilot.com/mcp/ \
        --header "Authorization: Bearer $GITHUB_TOKEN" \
        --transport http
    ```

## 6. Key Files & Directories

- **`Makefile`**: The entry point for all development and testing tasks.
- **`pyproject.toml`**: Defines Python project dependencies for Poetry.
- **`ansible.cfg`**: Main configuration file for Ansible.
- **`inventory/`**: Contains the Ansible inventory files.
- **`playbooks/`**: Contains the main Ansible playbooks.
- **`roles/`**: Contains all Ansible roles, where the main configuration tasks are defined.
- **`molecule/`**: Contains Molecule testing configurations within each role.
