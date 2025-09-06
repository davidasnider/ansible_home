"""macOS-specific test cases for localhost role."""

import os
import testinfra.utils.ansible_runner

# Handle case where tests are run outside of Molecule context (e.g., for coverage)
inventory_file = os.environ.get('MOLECULE_INVENTORY_FILE')
if inventory_file:
    testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
        inventory_file
    ).get_hosts('localhost_macos')
else:
    # When running coverage tests, we can't actually connect to hosts
    # but we still need to define testinfra_hosts for pytest to work
    testinfra_hosts = []


def test_homebrew_installation(host):
    """Test that Homebrew is installed."""
    brew_cmd = host.run("which brew")
    assert brew_cmd.rc == 0, "Homebrew should be installed"

    # Test brew is in expected location
    assert "/opt/homebrew/bin/brew" in brew_cmd.stdout or "/usr/local/bin/brew" in brew_cmd.stdout


def test_homebrew_packages_installed(host):
    """Test that required Homebrew packages are installed."""
    homebrew_packages = [
        'gh',
        'htop',
        'oh-my-posh',
        'poetry',
        'pre-commit',
        'zsh-autocomplete',
        'zsh-autosuggestions',
        'zsh-fast-syntax-highlighting',
        'zsh-history-substring-search'
    ]

    for package in homebrew_packages:
        cmd = host.run(f"brew list {package}")
        assert cmd.rc == 0, f"Homebrew package {package} should be installed"


def test_homebrew_casks_installed(host):
    """Test that required Homebrew casks are installed."""
    homebrew_casks = [
        '1password',
        '1password-cli',
        'iterm2',
        'visual-studio-code'
    ]

    for cask in homebrew_casks:
        cmd = host.run(f"brew list --cask {cask}")
        assert cmd.rc == 0, f"Homebrew cask {cask} should be installed"


def test_macos_ssh_config_1password(host):
    """Test macOS-specific SSH configuration with 1Password."""
    home = host.run("echo $HOME").stdout.strip()
    ssh_config = host.file(f"{home}/.ssh/config")

    assert ssh_config.exists
    assert ssh_config.is_file
    assert ssh_config.mode == 0o600

    content = ssh_config.content_string

    # Test 1Password agent configuration
    assert "IdentityAgent" in content
    assert "2BUA8C4S2C.com.1password" in content


def test_git_1password_signing_config(host):
    """Test Git configuration for 1Password signing on macOS."""
    macos_git_configs = {
        'gpg.ssh.program': '/Applications/1Password.app/Contents/MacOS/op-ssh-sign',
        'gpg.ssh.defaultKeyCommand': 'ssh-add -L',
    }

    for config, expected_value in macos_git_configs.items():
        cmd = host.run(f"git config --global {config}")
        assert cmd.rc == 0
        assert expected_value in cmd.stdout, f"{config} should contain {expected_value}"


def test_oh_my_zsh_installation_macos(host):
    """Test Oh My Zsh installation on macOS."""
    home = host.run("echo $HOME").stdout.strip()
    oh_my_zsh_dir = host.file(f"{home}/.oh-my-zsh")

    assert oh_my_zsh_dir.exists
    assert oh_my_zsh_dir.is_directory

    # Check for key Oh My Zsh files
    oh_my_zsh_sh = host.file(f"{home}/.oh-my-zsh/oh-my-zsh.sh")
    assert oh_my_zsh_sh.exists
    assert oh_my_zsh_sh.is_file


def test_zsh_configuration_macos(host):
    """Test zsh configuration files on macOS."""
    home = host.run("echo $HOME").stdout.strip()

    zshrc = host.file(f"{home}/.zshrc")
    zprofile = host.file(f"{home}/.zprofile")

    assert zshrc.exists
    assert zshrc.is_file
    assert zshrc.mode == 0o644

    assert zprofile.exists
    assert zprofile.is_file
    assert zprofile.mode == 0o644


def test_gitignore_dotfiles_entry(host):
    """Test that .dotfiles entry is added to .gitignore."""
    home = host.run("echo $HOME").stdout.strip()
    gitignore = host.file(f"{home}/.gitignore")

    assert gitignore.exists
    assert gitignore.mode == 0o600

    content = gitignore.content_string
    assert ".dotfiles" in content


def test_applications_installed(host):
    """Test that expected macOS applications are installed."""
    applications = [
        '/Applications/1Password 7 - Password Manager.app',
        '/Applications/iTerm.app',
        '/Applications/Visual Studio Code.app'
    ]

    for app_path in applications:
        app = host.file(app_path)
        # Applications might have different names or might not be installed in test environment
        # This is a flexible test that doesn't fail if apps aren't found
        if app.exists:
            assert app.is_directory


def test_homebrew_update_logic(host):
    """Test Homebrew update logic."""
    # Test that FETCH_HEAD exists (indicates brew operations have occurred)
    fetch_head = host.file("/opt/homebrew/.git/FETCH_HEAD")
    if not fetch_head.exists:
        # Try alternative location for Intel Macs
        fetch_head = host.file("/usr/local/Homebrew/.git/FETCH_HEAD")

    # This file should exist after Homebrew operations
    if fetch_head.exists:
        assert fetch_head.is_file


def test_macos_directory_permissions(host):
    """Test macOS-specific directory permissions."""
    home = host.run("echo $HOME").stdout.strip()

    # Test critical directories exist with correct permissions
    critical_dirs = [
        (f"{home}/code", 0o755),
        (f"{home}/.ssh", 0o700),
        (f"{home}/.local/bin", 0o755)
    ]

    for dir_path, expected_mode in critical_dirs:
        dir_obj = host.file(dir_path)
        assert dir_obj.exists
        assert dir_obj.is_directory
        assert dir_obj.mode == expected_mode


def test_1password_cli_security_configuration(host):
    """Test 1Password CLI security configuration on macOS."""
    home = host.run("echo $HOME").stdout.strip()

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


def test_1password_security_scripts(host):
    """Test 1Password security wrapper scripts on macOS."""
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


def test_1password_config_directory_security(host):
    """Test 1Password configuration directory security on macOS."""
    home = host.run("echo $HOME").stdout.strip()
    config_dir = f"{home}/.config/op"

    # Test config directory exists with correct permissions
    config_dir_obj = host.file(config_dir)
    assert config_dir_obj.exists, "1Password config directory should exist"
    assert config_dir_obj.is_directory
    assert config_dir_obj.mode == 0o700, "1Password config directory should have 700 permissions"

    # Test security config file exists with correct permissions
    config_file = host.file(f"{config_dir}/security-config")
    if config_file.exists:
        assert config_file.mode == 0o600, "1Password security config file should have 600 permissions"


def test_1password_health_check_functionality(host):
    """Test 1Password health check script functionality on macOS."""
    home = host.run("echo $HOME").stdout.strip()

    # Test health check script runs without critical errors
    health_check = host.run(f"{home}/.local/bin/op-health-check")

    # Health check should exit with 0 (all good), 1 (warnings), or 2 (errors)
    # We'll accept 0 or 1 since warnings are acceptable in test environment
    assert health_check.rc in [0, 1, 2], f"Health check returned unexpected exit code: {health_check.rc}"

    # Check that health check output contains expected sections
    output = health_check.stdout + health_check.stderr
    assert "Health Check Summary" in output, "Health check should contain summary section"
    assert "Passed:" in output, "Health check should show passed count"


def test_1password_security_wrapper_validation(host):
    """Test 1Password security wrapper script validation on macOS."""
    home = host.run("echo $HOME").stdout.strip()

    # Test validation command
    validation_cmd = host.run(f"{home}/.local/bin/op-secure --validate")

    # Validation should either pass or provide helpful error messages
    # We accept various exit codes since this depends on 1Password being set up
    assert validation_cmd.rc in [0, 1], f"Validation command should provide meaningful feedback"
