# Pull Request Approval Process

## Overview
This repository enforces strict quality gates through automated testing before any code can be merged to the main branch. All Pull Requests must pass comprehensive Molecule tests and receive manual approval.

## 🛡️ Branch Protection Rules (Managed by Pulumi)

The `main` branch is protected with the following requirements configured in `infrastructure/__main__.py`:

### Required Status Checks
All of the following automated checks must pass before a PR can be approved:

#### Core Molecule Testing Suite
- ✅ **Lint Ansible Code** - Ansible-lint validation across all roles
- ✅ **Molecule Test - default** - Cross-platform testing (Ubuntu, Debian)
- ✅ **Molecule Test - linux** - Linux-specific functionality testing
- ✅ **Molecule Test - idempotence** - Ensures tasks don't make unnecessary changes
- ✅ **All Molecule Tests** - Aggregate status of all test scenarios

#### Coverage & Quality
- ✅ **Test Coverage Report** - Test coverage analysis and reporting

#### Legacy Checks (if configured)
- 📝 Ansible Linting
- 🔒 Pre-commit Checks
- 🔍 Secret Scanning
- ✅ Ansible Syntax Check
- 📦 Dependency Review

### Review Requirements
- **Required Approving Reviews**: 1 approving review minimum
- **Dismiss Stale Reviews**: `true` - Reviews are dismissed when new commits are pushed
- **Require Code Owner Reviews**: `false` - Any repository collaborator can approve
- **Conversation Resolution**: All PR conversations must be resolved before merge

### Additional Protections
- **Require Signed Commits**: `true` - All commits must be GPG signed
- **Require Linear History**: `true` - No merge commits, only squash/rebase
- **Allow Force Pushes**: `false` - Force pushes to main branch are blocked
- **Allow Deletions**: `false` - Main branch cannot be deleted

## 🔄 PR Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# Make your changes
git commit -S -m "Your signed commit message"
git push origin feature/your-feature-name
```

### 2. Open Pull Request
When you open a PR to `main`, the following happens automatically:

1. **GitHub Actions Triggered**: The Molecule testing workflow starts
2. **Test Matrix Execution**: Multiple test scenarios run in parallel:
   - Linting validation
   - Default cross-platform tests
   - Linux-specific tests
   - Idempotency verification
   - Coverage analysis

### 3. Status Check Monitoring
Monitor the PR status checks in the GitHub UI:

```
🟡 Lint Ansible Code - In Progress
🟡 Molecule Test - default - Queued
🟡 Molecule Test - linux - Queued
🟡 Molecule Test - idempotence - Queued
🟡 All Molecule Tests - Pending
```

### 4. Test Results
Tests will complete with one of these states:

#### ✅ All Tests Pass
```
✅ Lint Ansible Code - Passed
✅ Molecule Test - default - Passed
✅ Molecule Test - linux - Passed
✅ Molecule Test - idempotence - Passed
✅ All Molecule Tests - Passed
✅ Test Coverage Report - Passed
```

**PR Status**: ✅ Ready for review and approval

#### ❌ Tests Fail
```
✅ Lint Ansible Code - Passed
❌ Molecule Test - default - Failed
🟡 Molecule Test - linux - Cancelled
🟡 Molecule Test - idempotence - Cancelled
❌ All Molecule Tests - Failed
```

**PR Status**: ❌ Cannot be approved until tests pass

### 5. Manual Review & Approval
Once all automated tests pass:

1. **Reviewer Assignment**: Request review from repository collaborators
2. **Code Review**: Reviewer examines changes for:
   - Code quality and best practices
   - Security implications
   - Documentation completeness
   - Architectural soundness

3. **Approval**: Reviewer approves the PR if satisfied
4. **Conversation Resolution**: All PR discussions must be resolved

### 6. Merge Process
After approval and all checks passing:

1. **Merge Button Enabled**: GitHub enables the merge button
2. **Merge Method**: Choose from:
   - **Squash and Merge** (recommended) - Clean commit history
   - **Rebase and Merge** - Preserve individual commits
   - **Create Merge Commit** - Traditional merge approach

3. **Automatic Cleanup**: Branch is automatically deleted after merge

## 🚫 What Prevents PR Approval

### Automated Blocks
- Any failing status check
- Unsigned commits (if signed commits required)
- Unresolved security alerts

### Manual Blocks
- No approving reviews
- Unresolved conversations
- Reviewer requests changes

## 🛠️ Managing Branch Protection

Branch protection rules are managed as code in `infrastructure/__main__.py`:

```python
# Branch protection for main branch
branch_protection = github.BranchProtection(
    "main-protection",
    repository_id=repo.node_id,
    pattern="main",
    required_status_checks=github.BranchProtectionRequiredStatusCheckArgs(
        strict=True,
        contexts=[
            "Lint Ansible Code",
            "Molecule Test - default",
            "Molecule Test - linux",
            "Molecule Test - idempotence",
            "All Molecule Tests",
            "Test Coverage Report",
        ],
    ),
    # ... other settings
)
```

### Updating Protection Rules
To modify branch protection:

1. Edit `infrastructure/__main__.py`
2. Run `pulumi up` to apply changes
3. Verify new rules in GitHub repository settings

## 📊 Testing Infrastructure

### Test Scenarios
- **default**: Cross-platform compatibility (Ubuntu, Debian)
- **linux**: Linux-specific package management and services
- **idempotence**: Ensures Ansible tasks are idempotent
- **macos**: macOS-specific testing (when available)

### Coverage Requirements
- Minimum test coverage thresholds enforced
- HTML and XML coverage reports generated
- Coverage trends tracked over time

### Local Testing
Run tests locally before pushing:

```bash
# Run all tests
make test

# Run specific scenario
make test-molecule-scenario SCENARIO=default

# Run with coverage
make test-coverage
```

## 🔍 Troubleshooting Failed Checks

### Linting Failures
```bash
# Fix linting issues locally
uv run ansible-lint roles/
```

### Molecule Test Failures
```bash
# Debug specific test scenario
cd roles/localhost
uv run molecule test -s default --debug

# Check test logs
uv run molecule verify -s default
```

### Coverage Issues
```bash
# Generate local coverage report
make test-coverage
open htmlcov/index.html
```

## 📈 Continuous Improvement

The testing infrastructure is continuously improved:

- New test scenarios added as the codebase grows
- Coverage requirements adjusted based on project needs
- Performance optimizations for faster CI/CD cycles
- Integration with additional quality tools

This process ensures that all code merged to main meets the highest quality standards while maintaining the ability to move quickly and safely.
