# Janitor journal

## 2026-11-21 - Removed unused install-oh-my-zsh.yml
**Learning:** All `include_tasks` in this repo are static filenames (verified across roles/ and playbooks/), so a single `grep -rn "file" --include="*.yml"` plus the full include graph is enough to prove a task file orphan. README.md lags reality: its directory tree (line 56) and line 314 still reference `roles/workstation/tasks/install-oh-my-zsh.yml` (deleted 2026-11-21) and describe the Oh My Zsh install as "extracted" there, while the live installs are inlined in `local-mac.yml` and `local-linux-shell.yml`. Check README claims against the real include graph before trusting them, and consider a scribe pass for that tree.
