# Palette UX Journal

## 2026-10-12 - CLI Feedback for Environment Variable Injection
**Learning:** Silent execution of CLI secret loading tools leaves users uncertain whether operations succeeded or silently skipped variables. Providing instant, clean confirmation with count metrics reassures users without exposing sensitive secret values.
**Action:** Always include non-verbose, informative success confirmations for interactive terminal functions.

## 2026-10-19 - Clear CLI Progress Indication
**Learning:** Lengthy setup scripts without clear progress indicators can leave users wondering if a process has stalled or failed silently.
**Action:** Add clear, numbered progress steps, ideally with relevant emojis, to CLI scripts to provide continuous feedback on the execution flow.

## 2026-10-19 - Fail Fast on Missing Dependencies
**Learning:** Allowing a script to proceed when critical commands (like `uv`) are missing results in confusing errors further down the line that are harder to debug.
**Action:** Explicitly check for the presence of critical commands (e.g., using `command -v`) early in the execution and fail fast with an actionable error message if they are not found.
