## 2024-05-24 - Environment Variable Leakage
**Vulnerability:** The bootstrap.sh script exported the user's sudo password as the ANSIBLE_SUDO_PASS environment variable and did not clean it up after execution.
**Learning:** Sensitive variables left in the environment can be accessed by child processes or linger in memory longer than necessary, increasing the attack surface.
**Prevention:** Always pass environment variables containing sensitive secrets (like passwords or tokens) inline to the commands that require them, rather than exporting them globally in the script.
