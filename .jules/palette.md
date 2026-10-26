# Palette UX Journal

## 2026-10-12 - CLI Feedback for Environment Variable Injection
**Learning:** Silent execution of CLI secret loading tools leaves users uncertain whether operations succeeded or silently skipped variables. Providing instant, clean confirmation with count metrics reassures users without exposing sensitive secret values.
**Action:** Always include non-verbose, informative success confirmations for interactive terminal functions.

## 2026-10-12 - Pre-check Validation and Platform Guidance in CLI Setup Scripts
**Learning:** Shell bootstrap scripts executed in incompatible OS environments often fail with cryptic system error messages (e.g. `sudo: apt: command not found`). Adding explicit package manager pre-checks provides instant, actionable guidance directing users to alternative setup targets without trial and error.
**Action:** Include early environment pre-checks with helpful alternative instructions in platform-specific bootstrap scripts.
