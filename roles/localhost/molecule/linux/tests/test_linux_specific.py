"""Linux-specific test cases for localhost role."""

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


def test_basic_git_configuration(host):
    """Test basic Git configuration that's applied in Linux scenario."""
    # Test user name configuration
    cmd = host.run("git config --global user.name")
    assert cmd.rc == 0
    assert cmd.stdout.strip() == "David Snider"

    # Test user email configuration
    cmd = host.run("git config --global user.email")
    assert cmd.rc == 0
    assert cmd.stdout.strip() == "david@davidsnider.org"


def test_directory_structure(host):
    """Test that required directory structure is created."""
    home = "/root"

    required_dirs = [
        f"{home}/code",
        f"{home}/.ssh",
        f"{home}/.local/bin"
    ]

    for dir_path in required_dirs:
        dir_obj = host.file(dir_path)
        assert dir_obj.exists, f"Directory {dir_path} should exist"
        assert dir_obj.is_directory, f"{dir_path} should be a directory"


def test_environment_variables_setup(host):
    """Test environment variables are properly configured."""
    # Test HOME environment variable
    cmd = host.run("echo $HOME")
    assert cmd.rc == 0
    assert cmd.stdout.strip() != ""

    # Test that we can run basic commands
    cmd = host.run("pwd")
    assert cmd.rc == 0
