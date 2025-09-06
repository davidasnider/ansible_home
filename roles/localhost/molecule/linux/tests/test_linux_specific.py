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


def test_1password_cli_installation_and_security(host):
    """Test 1Password CLI installation and security on Linux."""
    # Test 1Password CLI is installed
    op_cmd = host.run("which op")
    assert op_cmd.rc == 0, "1Password CLI should be installed"

    # Test CLI version meets minimum requirements
    version_cmd = host.run("op --version")
    assert version_cmd.rc == 0
    version_output = version_cmd.stdout

    # Extract version number and check it's 2.x.x or higher
    import re
    version_match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_output)
    assert version_match is not None, f"Could not parse version from: {version_output}"

    major_version = int(version_match.group(1))
    assert major_version >= 2, f"1Password CLI version {version_output} should be 2.x.x or higher"


def test_1password_gpg_keyring_security(host):
    """Test 1Password GPG keyring security on Linux."""
    # Test keyring file exists with correct permissions
    keyring_file = host.file("/usr/share/keyrings/1password-archive-keyring.gpg")
    assert keyring_file.exists, "1Password GPG keyring should exist"
    assert keyring_file.mode == 0o644, "GPG keyring should have 644 permissions"
    assert keyring_file.user == "root", "GPG keyring should be owned by root"
    assert keyring_file.group == "root", "GPG keyring should be group owned by root"


def test_1password_security_scripts_linux(host):
    """Test 1Password security wrapper scripts on Linux."""
    home = host.run("echo $HOME").stdout.strip()

    # Test security scripts exist and are executable
    security_scripts = [
        f"{home}/.local/bin/op-secure",
        f"{home}/.local/bin/op-health-check"
    ]

    for script_path in security_scripts:
        script_file = host.file(script_path)
        assert script_file.exists, f"Security script should exist: {script_path}"
        assert script_file.is_file
        assert script_file.mode == 0o755, f"Security script should be executable: {script_path}"


def test_1password_config_directory_security_linux(host):
    """Test 1Password configuration directory security on Linux."""
    home = host.run("echo $HOME").stdout.strip()
    config_dir = f"{home}/.config/op"

    # Test config directory exists with correct permissions
    config_dir_obj = host.file(config_dir)
    assert config_dir_obj.exists, "1Password config directory should exist"
    assert config_dir_obj.is_directory
    assert config_dir_obj.mode == 0o700, "1Password config directory should have 700 permissions"

    # Test config file exists with correct permissions
    config_file = host.file(f"{config_dir}/config")
    if config_file.exists:
        assert config_file.mode == 0o600, "1Password config file should have 600 permissions"


def test_1password_apt_repository_security(host):
    """Test 1Password APT repository security configuration on Linux."""
    # Test repository file exists
    repo_file = host.file("/etc/apt/sources.list.d/1password.list")
    assert repo_file.exists, "1Password repository should be configured"

    # Test repository uses signed-by keyring
    content = repo_file.content_string
    assert "signed-by=/usr/share/keyrings/1password-archive-keyring.gpg" in content, \
           "Repository should use signed keyring for verification"
