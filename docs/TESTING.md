# Testing Documentation

This document describes the comprehensive testing infrastructure for the ansible_home project using Molecule and pytest.

## Overview

The testing suite includes:
- **Molecule** for testing Ansible roles across different environments
- **Testinfra** for infrastructure testing
- **pytest** for test execution and coverage reporting
- **ansible-lint** for code quality assurance
- **CI/CD integration** with GitHub Actions

## Test Scenarios

### 1. Default Scenario (`default`)
- **Purpose**: General testing with Ubuntu and CentOS containers
- **Platforms**: Ubuntu 22.04, CentOS 8
- **Focus**: Basic functionality and cross-distribution compatibility

### 2. Linux Scenario (`linux`)
- **Purpose**: Comprehensive Linux testing across multiple distributions
- **Platforms**: Ubuntu 20.04, Ubuntu 22.04, Debian 11
- **Focus**: Linux-specific functionality and package management

### 3. Idempotence Scenario (`idempotence`)
- **Purpose**: Verify that Ansible tasks are idempotent
- **Platforms**: Ubuntu 22.04
- **Focus**: Ensuring tasks don't make unnecessary changes on repeat runs

### 4. macOS Scenario (`macos`)
- **Purpose**: Test macOS-specific functionality
- **Driver**: Delegated (requires macOS environment)
- **Focus**: Homebrew, 1Password integration, macOS-specific configurations

## Running Tests

### Prerequisites
```bash
# Install dependencies
make dev-setup
```

### Quick Testing
```bash
# Run linting and basic tests
make test

# Run all tests including coverage
make test-all
```

### Individual Test Scenarios
```bash
# Test specific scenario
make test-molecule-scenario SCENARIO=default
make test-molecule-scenario SCENARIO=linux
make test-molecule-scenario SCENARIO=idempotence
make test-molecule-scenario SCENARIO=macos
```

### Manual Molecule Commands
```bash
# Create test environment
make molecule-create

# Run playbook
make molecule-converge

# Run tests
make molecule-verify

# Destroy test environment
make molecule-destroy
```

### Coverage Testing
```bash
# Generate coverage reports
make test-coverage

# View HTML coverage report
open htmlcov/index.html
```

## Test Structure

```
roles/localhost/molecule/
├── default/                 # Default test scenario
│   ├── molecule.yml        # Molecule configuration
│   ├── converge.yml        # Test playbook
│   ├── prepare.yml         # Environment preparation
│   └── tests/
│       └── test_default.py # Test cases
├── linux/                  # Linux-specific tests
├── idempotence/             # Idempotency tests
└── macos/                   # macOS-specific tests
```

## Test Categories

### Infrastructure Tests
- Directory creation and permissions
- File existence and content verification
- Service status and configuration
- Package installation verification

### Security Tests
- SSH configuration validation
- Git security settings verification
- File permission checks
- Cryptographic key validation

### Idempotency Tests
- Configuration stability across runs
- No unnecessary changes detection
- State consistency verification

### Platform-Specific Tests
- **Linux**: Package managers, systemd services, shell configurations
- **macOS**: Homebrew packages, 1Password integration, macOS applications

## CI/CD Integration

### GitHub Actions Workflow
The `.github/workflows/molecule.yml` workflow:
1. **Lint Stage**: Runs ansible-lint on all roles
2. **Test Matrix**: Executes multiple scenarios in parallel
3. **Coverage**: Generates and uploads coverage reports

### Workflow Triggers
- Push to `main` or `develop` branches
- Pull requests to `main`
- Changes to role files, molecule configurations, or workflows

## Test Configuration

### pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
testpaths = ["roles/localhost/molecule", "tests"]
addopts = [
    "--cov=roles",
    "--cov-report=html",
    "--cov-report=xml",
    "--html=reports/pytest_report.html"
]
```

### Coverage Configuration
- **Source**: `roles/` directory
- **Exclude**: Test files, cache directories
- **Reports**: HTML, XML, and terminal output

## Writing New Tests

### Test File Structure
```python
"""Test cases for specific functionality."""

import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('target_group')

def test_functionality(host):
    """Test specific functionality."""
    # Test implementation
    assert condition, "Error message"
```

### Test Guidelines
1. **Descriptive Names**: Use clear, descriptive test function names
2. **Single Responsibility**: Each test should verify one specific aspect
3. **Error Messages**: Provide meaningful assertion messages
4. **Platform Awareness**: Consider platform differences in tests
5. **Idempotency**: Ensure tests can run multiple times safely

## Troubleshooting

### Common Issues

#### Docker Permission Issues
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Molecule Container Issues
```bash
# Clean up containers and volumes
make clean-test
docker system prune -f
```

#### Test Failures
```bash
# Run specific test with verbose output
cd roles/localhost
poetry run molecule test -s default --debug
```

### Debugging Tests
```bash
# Connect to test container for debugging
docker exec -it <container_name> /bin/bash

# View container logs
docker logs <container_name>
```

## Performance Considerations

### Test Optimization
- Use `pre_build_image: true` for faster container startup
- Cache Python dependencies in CI/CD
- Run scenarios in parallel where possible
- Use smaller base images when appropriate

### Resource Requirements
- **Memory**: Minimum 2GB for Docker containers
- **Disk**: ~5GB for container images and test artifacts
- **CPU**: Tests benefit from multi-core systems

## Future Enhancements

### Planned Improvements
1. **Performance Testing**: Add benchmarking for slow operations
2. **Security Scanning**: Integrate security vulnerability scans
3. **Multi-Architecture**: Test on ARM64 and AMD64 platforms
4. **Network Testing**: Verify network configurations and connectivity
5. **Backup/Recovery**: Test backup and restore procedures

### Integration Opportunities
- **Kubernetes**: Test deployments in K8s environments
- **Cloud Platforms**: Test on AWS, Azure, GCP instances
- **Monitoring**: Integration with monitoring and alerting systems
