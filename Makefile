dev-setup:
	@if ! command -v /opt/homebrew/bin/brew >/dev/null 2>&1; then \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
		if [ -f "/opt/homebrew/bin/brew" ]; then \
			eval "$$(/opt/homebrew/bin/brew shellenv)"; \
		fi \
	fi
	@if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then \
		/opt/homebrew/bin/brew install python@3; \
		/opt/homebrew/bin/brew link python@3; \
	fi
	@if ! command -v poetry >/dev/null 2>&1; then \
		/opt/homebrew/bin/brew install poetry; \
	fi
	/opt/homebrew/bin/poetry env remove --all || true
	rm -rf .venv
	/opt/homebrew/bin/python3 -m venv .venv
	/opt/homebrew/bin/poetry install
