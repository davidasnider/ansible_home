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

# Testing targets
.PHONY: test test-all test-lint test-molecule test-coverage clean-test

test: test-lint test-molecule
	@echo "All tests completed successfully"

test-all: test-lint test-molecule test-coverage
	@echo "All tests and coverage completed successfully"

test-lint:
	@echo "Running ansible-lint..."
	poetry run ansible-lint roles/

test-molecule:
	@echo "Running all Molecule scenarios..."
	cd roles/localhost && poetry run molecule test --all

test-molecule-scenario:
	@echo "Running Molecule scenario: $(SCENARIO)"
	cd roles/localhost && poetry run molecule test -s $(SCENARIO)

test-coverage:
	@echo "Running test coverage analysis..."
	poetry run pytest roles/localhost/molecule/*/tests/ --cov=roles --cov-report=html --cov-report=xml --cov-report=term-missing

clean-test:
	@echo "Cleaning up test artifacts..."
	rm -rf htmlcov/
	rm -rf reports/
	rm -f coverage.xml
	rm -f .coverage
	cd roles/localhost && poetry run molecule cleanup --all || true
	cd roles/localhost && poetry run molecule destroy --all || true

# Molecule specific targets
molecule-create:
	cd roles/localhost && poetry run molecule create

molecule-converge:
	cd roles/localhost && poetry run molecule converge

molecule-verify:
	cd roles/localhost && poetry run molecule verify

molecule-destroy:
	cd roles/localhost && poetry run molecule destroy

molecule-test-default:
	cd roles/localhost && poetry run molecule test -s default

molecule-test-linux:
	cd roles/localhost && poetry run molecule test -s linux

molecule-test-idempotence:
	cd roles/localhost && poetry run molecule test -s idempotence

molecule-test-macos:
	cd roles/localhost && poetry run molecule test -s macos

molecule-test-macos-utm:
	@echo "Running Molecule macOS tests with UTM VM..."
	./scripts/utm-macos-test.sh test

# UTM VM management targets
utm-vm-start:
	@echo "Starting UTM macOS VM..."
	./scripts/utm-macos-test.sh start

utm-vm-stop:
	@echo "Stopping UTM macOS VM..."
	./scripts/utm-macos-test.sh stop

utm-vm-status:
	@echo "Checking UTM macOS VM status..."
	./scripts/utm-macos-test.sh status
