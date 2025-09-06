"""Idempotency test cases for localhost role."""

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


def test_file_permissions_stability(host):
    """Test that file permissions remain stable across runs."""
    home = "/root"

    # Test key files maintain their permissions
    files_permissions = [
        (f"{home}/.ssh", 0o700),
        (f"{home}/.ssh/allowed_signers", 0o644),
        (f"{home}/code", 0o755),
        (f"{home}/.local/bin", 0o755),
    ]

    for file_path, expected_mode in files_permissions:
        file_obj = host.file(file_path)
        if file_obj.exists:
            assert file_obj.mode == expected_mode, f"{file_path} should maintain mode {oct(expected_mode)}"


def test_git_config_stability(host):
    """Test that git configuration remains stable."""
    # Test that git configs are set correctly and consistently
    git_configs = {
        'user.name': 'David Snider',
        'user.email': 'david@davidsnider.org',
    }

    for config_key, expected_value in git_configs.items():
        cmd = host.run(f"git config --global {config_key}")
        assert cmd.rc == 0
        assert cmd.stdout.strip() == expected_value


def test_directory_structure_stability(host):
    """Test that directory structure remains consistent."""
    home = "/root"

    required_directories = [
        f"{home}/code",
        f"{home}/.ssh",
        f"{home}/.local/bin"
    ]

    for directory in required_directories:
        dir_obj = host.file(directory)
        assert dir_obj.exists, f"Directory {directory} should exist after multiple runs"
        assert dir_obj.is_directory, f"{directory} should be a directory"


def test_file_content_stability(host):
    """Test that file contents remain stable across runs."""
    home = "/root"

    # Test allowed_signers file content
    allowed_signers = host.file(f"{home}/.ssh/allowed_signers")
    if allowed_signers.exists:
        content = allowed_signers.content_string.strip()
        expected_content = "david@davidsnider.org ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWm36FodEyxXOXxqhkCj0YLDHkori4Dzmq3hI0PsrX9"
        assert content == expected_content, "SSH allowed signers content should remain stable"


def test_no_unnecessary_changes(host):
    """Test that subsequent runs don't make unnecessary changes."""
    # This test verifies the principle that well-written Ansible tasks
    # should not change anything on the second run if the first run succeeded

    # Check that basic operations are idempotent by verifying existence
    # rather than modification time (which would change on every run)
    home = "/root"

    stable_items = [
        (f"{home}/code", "directory"),
        (f"{home}/.ssh/allowed_signers", "file"),
        (f"{home}/.local/bin", "directory")
    ]

    for item_path, item_type in stable_items:
        item_obj = host.file(item_path)
        assert item_obj.exists, f"{item_path} should exist and be stable"

        if item_type == "directory":
            assert item_obj.is_directory
        elif item_type == "file":
            assert item_obj.is_file


def test_ownership_consistency(host):
    """Test that file ownership remains consistent across runs."""
    home = "/root"

    # Test that files are owned by the correct user
    owned_items = [
        f"{home}/code",
        f"{home}/.ssh",
        f"{home}/.local/bin"
    ]

    for item_path in owned_items:
        item_obj = host.file(item_path)
        if item_obj.exists:
            assert item_obj.user == "root", f"{item_path} should be owned by root user"
