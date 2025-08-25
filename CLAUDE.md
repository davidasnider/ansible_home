# Ansible Home Project Guidelines

## Core Rules

- **Always use Ansible**: Never manually copy files or make system changes - only use ansible commands
- **Repository info**: Owner: `davidasnider`, Repo: `ansible_home`
- **Issues & TODOs**: Use GitHub issues to track all feature requests and tasks
- **Package management**: Add packages to Ansible roles, not direct brew installs
- **PR workflow**: Always validate changes before creating PRs, let CI/CD handle merging

## Testing Commands

### Quick Development

```bash
make test-lint          # ⚡ 15s - YAML/syntax validation
make test               # 🟡 5-10min - Full Docker testing
```

### Complete Validation

```bash
make test-all           # 🔴 10-15min - Everything + coverage
```

### Individual Scenarios

```bash
make molecule-test-default       # Docker: Basic functionality
make molecule-test-linux         # Docker: Linux-specific
make molecule-test-idempotence   # Docker: Idempotency validation
make molecule-test-macos-utm     # UTM VM: macOS native (local only)
```

## When to Test

- **While coding**: `make test-lint` (fast feedback)
- **Before PR**: `make test-all` (recommended)
- **Major releases**: Include UTM macOS testing if available

## Automated Testing

- **Pre-commit**: Fast formatting checks (~10s)
- **CI Pipeline**: Full matrix testing on every PR (~12min)
- **Status checks**: Required before merge
