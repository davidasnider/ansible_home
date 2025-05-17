# TODO List

## 1. **Set Up the Repository**

- [x] Create a modular and reusable role-based design for playbooks.
- [x] Separate inventories, variables, and configurations for local and cloud targets.
- [x] Secure secrets management by integrating HashiCorp Vault (and optionally Ansible Vault as a fallback).

## 2. **Establish Directory Structure**

- [x] Create the recommended directory structure:
  - [x] `.github/workflows/` for CI/CD workflows.
  - [x] `docs/` for project documentation.
  - [x] `inventory/` for environment-specific inventories.
  - [x] `playbooks/` for entry-point playbooks.
  - [x] `roles/` for Ansible roles.
  - [x] `group_vars/` and `host_vars/` for shared and host-specific variables.
  - [x] `vault/` for encrypted secrets.
  - [x] `library/` and `filter_plugins/` for custom modules and plugins.
  - [x] `tests/` for Molecule test scenarios.

## 3. **Set Up Python Environment**

- [x] Use Poetry for dependency management:
  - Initialize the project with `poetry init`.
  - Add dependencies like `ansible` and `hvac`.
- [x] Ensure contributors use the same virtual environment (`poetry shell`).

## 4. **Secrets Management**

- [ ] Integrate HashiCorp Vault for centralized secrets management.
- [ ] Document Vault usage in the `docs/` folder.
- [ ] Optionally, set up Ansible Vault for local fallback encryption.

## 5. **CI/CD and Testing**

- [ ] Set up GitHub Actions workflows:
  - Linting and syntax-checking workflow (`ansible-lint` and `ansible-playbook --syntax-check`).
  - Molecule testing workflow for roles.
- [ ] Use GitHub secrets for secure interactions with Vault or cloud providers.

## 6. **Automated Testing**

- [ ] Implement Ansible linting for playbooks and roles.
- [ ] Add syntax-checking as a preliminary step for pushes and pull requests.
- [ ] Use Molecule to test roles in isolated environments.

## 7. **Dynamic Inventories**

- [ ] Consider dynamic inventory scripts/plugins for cloud resources.

## 8. **Scalability and Extensibility**

- [ ] Introduce subdirectories in `roles/` for logical separation (e.g., `monitoring`, `logging`).
- [ ] Maintain `library/` and `filter_plugins/` for custom logic.

## 9. **Documentation**

- [ ] Create a comprehensive README.
- [ ] Add a `docs/` directory for design decisions and onboarding guides.
