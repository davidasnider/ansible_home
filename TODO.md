# TODO List

## 1. **Core Workstation Setup**
- [x] Standardize workstation role architecture (main.yml/roles syntax).
- [x] Implement "Pro-Lazy" Zsh initialization strategy.
- [x] Automated Nerd Font installation (Meslo LG M).
- [x] Python 3.12+ and Ansible 13 environment upgrade.

## 2. **Maintenance & Workflow**
- [x] Repository cleanup automation (`make cleanup`).
- [x] macOS workstation update skill.
- [x] Claude code review workflow (`@claude review` on a PR; actions pinned to commit SHAs).

## 3. **Raspberry Pis & Home Network**
- [x] Raspberry Pi baseline role (SSH hardening, ufw, unattended upgrades).
- [x] Add `bedroom-pi` (Wi-Fi power save disabled via a persistent systemd unit).
- [x] NUT server on `bedroom-pi`; the Mac is a NUT client (see [NUT Integration](docs/NUT_UPS_INTEGRATION.md)).
- [ ] Exercise the UPS shutdown path end to end (Mac `upsmon` secondary and Pi primary) during a planned power-loss test.
- [x] Molecule scenarios and a CI job for the `raspberry_pi` and `nut_server` roles (`make test-molecule`).

## 4. **Secrets Management**
- [x] Fetch secrets from 1Password at runtime (Pi sudo password, SSH public keys, NUT passwords), resolved once per run.
- [x] Document 1Password usage (`docs/1PASSWORD_SECURITY.md`).
- ~~HashiCorp Vault / Ansible Vault~~ Superseded: 1Password is the secrets store for this repo. Reopen only if a need appears that 1Password can't cover.

## 5. **CI/CD and Testing**
- [x] Implement syntax-checking as a gate for pushes (`Ansible Syntax Check` job in `ci.yml`).
- [x] GitHub Actions `Molecule` job in `ci.yml` (currently covers `raspberry_pi` and `nut_server`).
- [ ] Extend Molecule coverage to the `workstation` and `home_assistant_remote` roles (the existing `workstation` scenario only runs a few basic tasks and is not run in CI).
- [ ] Integrate Pulumi automation (CD) for infrastructure changes (`infrastructure/` exists, but no workflow runs it).

## 6. **Documentation**
- [x] Comprehensive README overhaul.
- [x] NUT UPS integration guide (`docs/NUT_UPS_INTEGRATION.md`).
- [ ] Create detailed onboarding guides in `docs/`.
- [ ] Add Architecture Decision Records (ADRs) for Pro-Lazy shell and Role structure.

## 7. **Scalability**
- [ ] Introduce subdirectories in `roles/` for logical separation (e.g., `monitoring`, `logging`).
- [ ] Maintain `library/` and `filter_plugins/` for custom logic (neither directory exists yet).
