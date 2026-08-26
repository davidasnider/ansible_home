## 2024-05-24 - Environment Variable Leakage
**Vulnerability:** The bootstrap.sh script exported the user's sudo password as the ANSIBLE_SUDO_PASS environment variable and did not clean it up after execution.
**Learning:** Sensitive variables left in the environment can be accessed by child processes or linger in memory longer than necessary, increasing the attack surface.
**Prevention:** Pass environment variables containing sensitive secrets (like passwords or tokens) inline to the commands that require them, rather than exporting them globally in the script. Note that this only limits the secret's scope to the shell session and that single command invocation — the command and its own child processes (e.g., Ansible modules doing an env lookup) can still read it. For stronger protection, prefer interactive prompts such as `--ask-become-pass` or a dedicated secret manager instead of passing secrets through the environment at all.

## 2024-08-18 - Sensitive Data Leakage in Logs
**Vulnerability:** The 1Password secure wrapper script (`op-secure`) logged the entire `op` command array (`$*`), including sensitive arguments like passwords and secret values, into a persistent log file (`~/.config/op/op-secure.log`).
**Learning:** Command-line parameters passed to wrapper scripts are often blindly logged for debugging purposes. When interacting with secret managers or authentication tools, these parameters frequently contain sensitive data that should never touch the disk in plaintext.
**Prevention:** Never log `$@` or `$*` when wrapping CLI tools that handle secrets. Always selectively log only safe parts of the command (e.g. just the subcommand, like `$1`) and omit the remaining arguments to prevent credential harvesting from log files.

## 2024-10-17 - Environment Variable Leakage in Bootstrap
**Vulnerability:** The `bootstrap.sh` script previously read the sudo password and passed it via the `ANSIBLE_SUDO_PASS` environment variable, exposing it to child processes and memory.
**Learning:** Hardcoding or passing secrets through environment variables in scripts introduces an unneeded attack surface.
**Prevention:** Native interactive tools (such as `--ask-become-pass` for Ansible) should be used instead of manual prompt loops combined with environment variables for secret ingestion.
