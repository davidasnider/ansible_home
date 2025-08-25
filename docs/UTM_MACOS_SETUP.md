# UTM macOS VM Setup for Molecule Testing

This document explains how to set up a UTM macOS virtual machine for running Molecule tests locally.

## Prerequisites

1. **UTM with CLI support** installed:
   ```bash
   brew install --cask utm
   ```

2. **macOS VM** already created in UTM (you mentioned you have this)

3. **SSH access** configured on the macOS VM

## VM Configuration

### 1. macOS VM Setup

Inside your macOS VM, ensure the following are configured:

#### Enable SSH
```bash
# Enable remote login
sudo systemsetup -setremotelogin on

# Verify SSH is running
sudo launchctl list | grep ssh
```

#### Install Required Tools
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3 (required for Ansible)
brew install python@3.11

# Ensure Python 3 is available at /usr/bin/python3
sudo ln -sf /opt/homebrew/bin/python3 /usr/bin/python3
```

#### Set up SSH Key Authentication
```bash
# On your host machine, copy your public key to the VM
ssh-copy-id -p 2222 username@127.0.0.1

# Or manually:
cat ~/.ssh/id_rsa.pub | ssh -p 2222 username@127.0.0.1 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 3. Create Baseline Snapshot

Once your VM is configured:

1. Shut down the VM cleanly
2. In UTM, right-click your VM → Snapshots
3. Create a new snapshot named `molecule-baseline`
4. This snapshot will be used as the clean state for testing

## Environment Configuration

Create a `.env` file in the project root (or set environment variables):

```bash
# UTM VM Configuration
export UTM_VM_NAME="macOS-Test"                    # Name of your UTM VM
export UTM_SNAPSHOT_NAME="molecule-baseline"       # Baseline snapshot name

# SSH Connection Settings
export MOLECULE_MACOS_HOST="127.0.0.1"            # UTM host IP
export MOLECULE_MACOS_PORT="2222"                 # SSH port forwarding
export MOLECULE_MACOS_USER="your-username"        # Username on the VM
export MOLECULE_MACOS_SSH_KEY="~/.ssh/id_rsa"     # SSH private key path
export MOLECULE_MACOS_PYTHON="/usr/bin/python3"   # Python interpreter path
```

## Usage

### Running Tests

#### Full Test Cycle (Recommended)
```bash
# This will: start VM from snapshot → run tests → cleanup
make molecule-test-macos-utm
```

#### Manual VM Management
```bash
# Start VM and wait for SSH
make utm-vm-start

# Check VM status
make utm-vm-status

# Run just the molecule test (assumes VM is running)
make molecule-test-macos

# Stop VM and restore snapshot
make utm-vm-stop
```

### Direct Script Usage

```bash
# Full test cycle
./scripts/utm-macos-test.sh test

# Individual commands
./scripts/utm-macos-test.sh start
./scripts/utm-macos-test.sh ssh     # Test SSH connectivity
./scripts/utm-macos-test.sh status
./scripts/utm-macos-test.sh stop
```

## Troubleshooting

### VM Won't Start
- Check that UTM is running
- Verify VM name matches `UTM_VM_NAME` setting
- Try starting the VM manually in UTM GUI first

### SSH Connection Failed
- Verify port forwarding is configured (2222 → 22)
- Test SSH manually: `ssh -p 2222 username@127.0.0.1`
- Check that SSH is enabled on the VM
- Verify SSH key authentication is working

### Python/Ansible Issues
- Ensure Python 3 is installed on the VM
- Verify the Python interpreter path: `MOLECULE_MACOS_PYTHON`
- Check that required Python modules are available

### UTM CLI Issues
```bash
# Check if UTM CLI is available
which utmctl

# List available VMs
utmctl list

# Check specific VM status
utmctl status "macOS-Test"
```

## CI/CD Integration

The configuration automatically detects the environment:

- **Local development**: Uses SSH connection to UTM VM
- **GitHub Actions**: Uses local connection on macOS runner

No changes needed in CI/CD - the GitHub Actions workflow is already configured to run macOS tests on `macos-latest` runners.

## Security Notes

- SSH host key checking is disabled for the test environment
- Use a dedicated test VM, not your main development machine
- The baseline snapshot ensures clean state for each test run
- Consider using a separate SSH key pair for VM testing

## Performance Tips

1. **Allocate sufficient resources** to the UTM VM:
   - RAM: At least 4GB (8GB recommended)
   - CPU: At least 2 cores
   - Storage: At least 50GB free space

2. **Optimize snapshot usage**:
   - Create snapshots with minimal running services
   - Keep the baseline snapshot clean and minimal

3. **Network performance**:
   - Use bridged networking if possible for better performance
   - Consider increasing SSH connection timeout for slower systems
