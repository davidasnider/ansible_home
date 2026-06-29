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

# Testing targets
.PHONY: test test-all test-lint test-syntax clean-test cleanup

test: test-lint test-syntax
	@echo "All tests completed successfully"

test-all: test
	@echo "Full suite completed"

test-lint:
	@echo "Running pre-commit formatting checks..."
	uv run pre-commit run --all-files
	@echo "Running ansible-lint..."
	uv run ansible-lint roles/

test-syntax:
	@echo "Checking playbook syntax..."
	uv run ansible-playbook --syntax-check -i inventory/hosts.yml site.yml

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
