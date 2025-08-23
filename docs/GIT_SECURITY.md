# Git Security Hardening Guide

This document outlines the comprehensive Git security hardening implemented in this repository to ensure all commits are properly signed, verified, and secured.

## 🔒 Security Features Implemented

### 1. Commit Signing Configuration

All commits and tags are now required to be signed using SSH keys managed by 1Password:

- **Commit signing enabled**: `commit.gpgsign = true`
- **Tag signing enabled**: `tag.gpgsign = true`
- **SSH signing format**: Using SSH keys instead of traditional GPG
- **1Password integration**: SSH signing handled by 1Password SSH agent

### 2. Enhanced Git Security Settings

The following security configurations have been applied:

```bash
# SSL/TLS Security
http.sslverify = true
http.sslversion = tlsv1.2

# Object verification
receive.fsckobjects = true
transfer.fsckobjects = true
fetch.fsckobjects = true

# SSH key validation
gpg.ssh.defaultKeyCommand = ssh-add -L
gpg.ssh.allowedSignersFile = ~/.ssh/allowed_signers
```

### 3. SSH Configuration Hardening

The SSH configuration has been enhanced with:

- **Strong cipher suites**: ChaCha20-Poly1305, AES-GCM
- **Strong MAC algorithms**: HMAC-SHA2-256/512 with ETM
- **Modern key exchange**: Curve25519, strong DH groups
- **Host key verification**: Strict checking enabled
- **Agent security**: Forward agent disabled, identities-only mode

### 4. Pre-commit Security Hooks

Automated security validation includes:

- **Commit signature verification**: Ensures all commits are properly signed
- **SSH key permission checks**: Validates private key permissions (600)
- **Allowed signers validation**: Verifies format of allowed_signers file

## 🔑 Key Management Procedures

### Current Signing Key

The repository uses the following SSH signing key:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKWm36FodEyxXOXxqhkCj0YLDHkori4Dzmq3hI0PsrX9
```

### Key Rotation Process

Use the provided key rotation script:

```bash
~/.local/bin/rotate-git-keys
```

This script will:
1. Backup current configuration
2. Display current keys and configuration
3. Provide instructions for adding new keys
4. Verify current Git configuration

### Manual Key Rotation Steps

1. **Generate new SSH key in 1Password**:
   - Create a new SSH key in 1Password
   - Ensure it's loaded in the SSH agent

2. **Update allowed_signers file**:
   ```bash
   echo 'david@davidsnider.org ssh-ed25519 <NEW_PUBLIC_KEY>' >> ~/.ssh/allowed_signers
   ```

3. **Update Git configuration**:
   ```bash
   git config --global user.signingkey 'ssh-ed25519 <NEW_PUBLIC_KEY>'
   ```

4. **Update Ansible configuration**:
   - Modify `roles/localhost/tasks/local-linux.yml`
   - Update the signing key in both the Git config and allowed_signers tasks

5. **Remove old key** (after verification):
   - Remove from allowed_signers file
   - Remove from 1Password if no longer needed

## 🛡️ Security Verification

### Verifying Commit Signatures

Check if commits are properly signed:

```bash
# Verify specific commit
git verify-commit <commit-hash>

# Verify current HEAD
git verify-commit HEAD

# Show signature information
git log --show-signature
```

### Validating Configuration

Check current security configuration:

```bash
# View all security-related Git config
git config --list | grep -E "(gpg|ssh|ssl|fsck)"

# Verify SSH configuration
ssh -T git@github.com

# Check allowed signers
cat ~/.ssh/allowed_signers
```

### Pre-commit Hook Testing

Test security hooks manually:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run security hooks only
pre-commit run verify-commit-signature
pre-commit run check-ssh-key-permissions
pre-commit run validate-allowed-signers
```

## 🚨 Security Requirements

### For Contributors

All contributors must:

1. **Sign all commits** with a verified SSH key
2. **Use strong SSH keys** (Ed25519 recommended, minimum RSA 4096-bit)
3. **Keep private keys secure** using hardware tokens or secure key managers
4. **Verify signatures** before pushing changes

### For Repository Maintainers

Repository maintainers should:

1. **Regularly rotate signing keys** (recommended every 6 months)
2. **Monitor commit signatures** in pull requests
3. **Update allowed signers** when team members change
4. **Review security configuration** during updates

## 🔧 Troubleshooting

### Common Issues

1. **Commit signing fails**:
   - Ensure 1Password SSH agent is running
   - Verify signing key is loaded: `ssh-add -L`
   - Check Git configuration: `git config --list | grep gpg`

2. **SSH connection fails**:
   - Verify SSH config syntax
   - Test connection: `ssh -T git@github.com`
   - Check SSH agent: `ssh-add -l`

3. **Pre-commit hooks fail**:
   - Update pre-commit: `pre-commit install`
   - Check hook syntax: `pre-commit run --all-files`

### Emergency Procedures

If signing becomes unavailable:

1. **Temporary bypass** (emergency only):
   ```bash
   git commit --no-gpg-sign -m "Emergency commit - signing unavailable"
   ```

2. **Re-sign commits** after fixing:
   ```bash
   git commit --amend --gpg-sign
   git rebase --exec 'git commit --amend --no-edit --gpg-sign' HEAD~N
   ```

## 📚 Additional Resources

- [Git Signing Documentation](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- [SSH Security Best Practices](https://stribika.github.io/2015/01/04/secure-secure-shell.html)
- [1Password SSH Agent](https://developer.1password.com/docs/ssh/)

---

**Note**: This security configuration is designed to provide defense-in-depth protection for Git operations while maintaining usability for daily development workflows.
