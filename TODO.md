# TODO List

## 3. **Where we left off**
- [ ] Add the nerd fonts for the terminal.

## 4. **Secrets Management**

- [ ] Secure secrets management by integrating HashiCorp Vault (and optionally Ansible Vault as a fallback).
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
