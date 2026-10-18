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
	@if ! command -v uv >/dev/null 2>&1; then \
		/opt/homebrew/bin/brew install uv; \
	fi
	rm -rf .venv
	uv sync
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg --overwrite

# Testing targets
.PHONY: test test-all test-lint test-syntax test-molecule molecule-test-raspberry-pi molecule-test-nut-server clean-test cleanup check-updates

test: test-lint test-syntax
	@echo "All tests completed successfully"

test-all: test test-molecule
	@echo "Full suite completed"

# Molecule scenarios need a running Docker daemon. With OrbStack the Python Docker
# SDK does not read the CLI context, so export DOCKER_HOST first, e.g.
#   export DOCKER_HOST=unix://$$HOME/.orbstack/run/docker.sock
test-molecule: molecule-test-raspberry-pi molecule-test-nut-server

molecule-test-raspberry-pi:
	@echo "Running Molecule for the raspberry_pi role..."
	cd roles/raspberry_pi && uv run molecule test

molecule-test-nut-server:
	@echo "Running Molecule for the nut_server role..."
	cd roles/nut_server && uv run molecule test

test-lint:
	@echo "Running pre-commit formatting checks..."
	uv run pre-commit run --all-files
	@echo "Running ansible-lint..."
	uv run ansible-lint roles/

test-syntax:
	@echo "Checking playbook syntax..."
	uv run ansible-playbook --syntax-check -i inventory/hosts.yml site.yml

check-updates:
	@echo "Checking for remote_homeassistant updates..."
	uv run python scripts/check_updates.py

cleanup:
	@echo "Running repository cleanup..."
	@awk '/^```bash/{flag=1;next}/^```/{flag=0}flag' .agents/skills/cleanup/SKILL.md | bash

clean-test:
	@echo "Cleaning up test artifacts..."
	rm -rf htmlcov/
	rm -rf reports/
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
