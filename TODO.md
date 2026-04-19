# TODO List

## 1. **Core Workstation Setup**
- [x] Standardize workstation role architecture (main.yml/roles syntax).
- [x] Implement "Pro-Lazy" Zsh initialization strategy.
- [x] Automated Nerd Font installation (Meslo LG M).
- [x] Python 3.12+ and Ansible 13 environment upgrade.

## 2. **Maintenance & Workflow**
- [x] Repository cleanup automation (`make cleanup`).
- [x] macOS workstation update skill.

## 3. **Secrets Management**
- [ ] Secure secrets management by integrating HashiCorp Vault (and optionally Ansible Vault as a fallback).
- [ ] Integrate HashiCorp Vault for centralized secrets management.
- [ ] Document Vault usage in the `docs/` folder.
- [ ] Optionally, set up Ansible Vault for local fallback encryption.

## 4. **CI/CD and Testing**
- [ ] Set up GitHub Actions workflow for **Molecule** testing.
  - Required for branch protection compliance.
- [ ] Implement syntax-checking as a gate for pushes.
- [ ] Integrate Pulumi automation (CD) for infrastructure changes.

## 5. **Documentation**
- [x] Comprehensive README overhaul.
- [ ] Create detailed onboarding guides in `docs/`.
- [ ] Add Architecture Decision Records (ADRs) for Pro-Lazy shell and Role structure.

## 6. **Scalability**
- [ ] Introduce subdirectories in `roles/` for logical separation (e.g., `monitoring`, `logging`).
- [ ] Maintain `library/` and `filter_plugins/` for custom logic.
