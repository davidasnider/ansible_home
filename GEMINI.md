# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the `ansible_home` project.

## Project Overview

This is an Ansible project designed to automate the setup and configuration of a local development environment on macOS and Linux. It uses Ansible to install software, configure system settings, and enforce security best practices.

The project is structured as follows:

-   **`playbooks/`**: Contains the main Ansible playbooks. `local-main.yml` is the entry point.
-   **`roles/`**: Contains the Ansible roles. The `localhost` role contains the main tasks for configuring the system.
-   **`molecule/`**: Contains Molecule tests for testing the Ansible roles in isolated environments (Docker).
-   **`Makefile`**: Provides a set of commands for common development and testing tasks.
-   **`pyproject.toml`**: Defines the Python project dependencies, managed with Poetry.
-   **`.pre-commit-config.yaml`**: Configures pre-commit hooks for code quality and security checks.

**Key Technologies:**

-   **Ansible**: For automation and configuration management.
-   **Python**: As the underlying language for Ansible and for scripting.
-   **Poetry**: For Python dependency management.
-   **Molecule**: For testing Ansible roles.
-   **pytest**: For running tests.
-   **pre-commit**: for running quality and security checks.
-   **Make**: For task automation.

## Building and Running

### Development Setup

To set up the development environment, run:

```bash
make dev-setup
```

This will install Homebrew, Python, and all the project dependencies using Poetry.

### Running the Playbook

To run the main playbook and apply the configuration to your local machine, run:

```bash
source .venv/bin/activate
ansible-playbook -i inventory/local.yml playbooks/local-main.yml
```

### Testing

The project has a comprehensive test suite using Molecule and pytest.

-   **Run all tests:**
    ```bash
    make test
    ```

-   **Run linting checks:**
    ```bash
    make test-lint
    ```

-   **Run Molecule tests:**
    ```bash
    make test-molecule
    ```

-   **Run tests in parallel (faster):**
    ```bash
    make test-fast
    ```

-   **Run a specific Molecule scenario:**
    ```bash
    make test-molecule-scenario SCENARIO=<scenario_name>
    ```
    (e.g., `SCENARIO=default`)

## Development Conventions

-   **Dependency Management**: Python dependencies are managed with Poetry and are defined in `pyproject.toml`.
-   **Linting and Formatting**: The project uses `pre-commit` to enforce code quality. Key tools include:
    -   `trailing-whitespace`
    -   `end-of-file-fixer`
    -   `check-yaml`
    -   `detect-secrets`
    -   `ansible-lint` (run via `make test-lint`)
-   **Commit Signatures**: All commits must be signed. A pre-commit hook enforces this.
-   **Testing**:
    -   Ansible roles are tested using Molecule. Test scenarios are defined in the `molecule/` directory within each role.
    -   Pytest is used for more complex test cases.
-   **Git Workflow**: The project follows standard Git practices. See `docs/PR_APPROVAL_PROCESS.md` for more details.
-   **Security**: The project includes several security-focused tasks, including SSH key management, Git security hardening, and 1Password integration.
