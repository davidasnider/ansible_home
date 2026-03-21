"""Test cases for default localhost role scenario."""

import os
import testinfra.utils.ansible_runner

# Handle case where tests are run outside of Molecule context (e.g., for coverage)
inventory_file = os.environ.get('MOLECULE_INVENTORY_FILE')
if inventory_file:
    testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
        inventory_file
    ).get_hosts('localhost_linux')
else:
    # When running coverage tests, we can't actually connect to hosts
    # but we still need to define testinfra_hosts for pytest to work
    testinfra_hosts = []


def test_code_directory_exists(host):
    """Test that the ~/code directory exists with correct permissions."""
    home = host.user().home
    code_dir = host.file(f"{home}/code")

    assert code_dir.exists
    assert code_dir.is_directory
    assert code_dir.mode == 0o755


def test_basic_git_configuration(host):
    """Test basic Git configuration that's applied in default scenario."""
    # Test user name configuration
    cmd = host.run("git config --global user.name")
    assert cmd.rc == 0
    assert cmd.stdout.strip() == "David Snider"

    # Test user email configuration
    cmd = host.run("git config --global user.email")
    assert cmd.rc == 0
    assert cmd.stdout.strip() == "david@davidsnider.org"

    # Test signing key configuration
    cmd = host.run("git config --global user.signingkey")
    assert cmd.rc == 0
    assert "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWm36FodEyxXOXxqhkCj0YLDHkori4Dzmq3hI0PsrX9" in cmd.stdout


def test_ssh_directory_structure(host):
    """Test basic SSH directory structure is present."""
    home = host.user().home
    ssh_dir = host.file(f"{home}/.ssh")

    # Test SSH directory exists and has correct permissions
    assert ssh_dir.exists
    assert ssh_dir.is_directory
    assert ssh_dir.mode == 0o700


def test_local_bin_directory(host):
    """Test that ~/.local/bin directory exists."""
    home = host.user().home
    local_bin = host.file(f"{home}/.local/bin")

    assert local_bin.exists
    assert local_bin.is_directory
    assert local_bin.mode == 0o755


def test_environment_setup(host):
    """Test basic environment setup."""
    # Test HOME environment variable
    cmd = host.run("echo $HOME")
    assert cmd.rc == 0
    assert cmd.stdout.strip() != ""

    # Test that we can run basic commands
    cmd = host.run("pwd")
    assert cmd.rc == 0
