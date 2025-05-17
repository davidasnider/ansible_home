dev-setup:
	@if ! command -v brew >/dev/null 2>&1; then \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
		if [ -f "/opt/homebrew/bin/brew" ]; then \
			eval "$$(/opt/homebrew/bin/brew shellenv)"; \
		fi \
	fi
	@if ! command -v python3 >/dev/null 2>&1; then \
		brew install python@3; \
		brew link python@3; \
	fi
	@if ! command -v poetry >/dev/null 2>&1; then \
		brew install poetry; \
	fi
	poetry env remove --all || true
	rm -rf .venv
	python3 -m venv .venv
	poetry install
