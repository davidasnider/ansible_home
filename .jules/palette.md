# Palette UX Journal

## 2026-10-12 - CLI Feedback for Environment Variable Injection
**Learning:** Silent execution of CLI secret loading tools leaves users uncertain whether operations succeeded or silently skipped variables. Providing instant, clean confirmation with count metrics reassures users without exposing sensitive secret values.
**Action:** Always include non-verbose, informative success confirmations for interactive terminal functions.

## 2026-10-12 - Pre-check Validation and Platform Guidance in CLI Setup Scripts
**Learning:** Shell bootstrap scripts executed in incompatible OS environments often fail with cryptic system error messages (e.g. `sudo: apt: command not found`). Adding explicit package manager pre-checks provides instant, actionable guidance directing users to alternative setup targets without trial and error.
**Action:** Include early environment pre-checks with helpful alternative instructions in platform-specific bootstrap scripts.

## 2026-10-19 - Clear CLI Progress Indication
**Learning:** Lengthy setup scripts without clear progress indicators can leave users wondering if a process has stalled or failed silently.
**Action:** Add clear, numbered progress steps, ideally with relevant emojis, to CLI scripts to provide continuous feedback on the execution flow.

## 2026-10-19 - Fail Fast on Missing Dependencies
**Learning:** Allowing a script to proceed when critical commands (like `uv`) are missing results in confusing errors further down the line that are harder to debug.
**Action:** Explicitly check for the presence of critical commands (e.g., using `command -v`) early in the execution and fail fast with an actionable error message if they are not found.

## 2026-10-27 - Actionable Remediation Output for CLI Diagnostics
**Learning:** Warning users about outdated dependencies or configuration mismatches without providing the exact target file path and YAML/config keys forces the user to manually search through roles. Presenting clear per-item status and ready-to-paste remediation snippets turns an alert directly into a fast, error-free fix.
**Action:** Always provide explicit config file paths and copy-pasteable remediation snippets alongside diagnostic warning alerts in CLI tools.
