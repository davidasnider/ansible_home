# Scribe Journal

## 2026-11-21 - Fixed stale "Ansible 11.5+" in README uv section
**Learning:** `pyproject.toml` is the source of truth for version pins (here: `ansible >=13.5.0,<14.0.0`,
Python `>=3.12`). README.md states the Ansible version in two places — "Key Technologies" (line ~12,
correct as "Ansible 13+") and the uv Configuration bullet (line ~141, was stale "Ansible 11.5+", now
fixed). TODO.md line 7 ("Python 3.12+ and Ansible 13 environment upgrade", checked) corroborates the
upgrade, making good cross-evidence for version claims. The README's macOS "Python 3.11+" line matches
the Makefile's own `sys.version_info >= (3, 11)` guard in dev-setup, so it was left as-is despite
`requires-python = ">=3.12"` — only flag it if the Makefile itself is considered wrong, since docs
should describe what `make dev-setup` actually does.
