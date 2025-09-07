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
.PHONY: test test-all test-lint test-molecule test-coverage clean-test test-fast test-prep docker-build-base

test: test-lint test-molecule
	@echo "All tests completed successfully"

test-all: test-lint test-molecule test-coverage
	@echo "All tests and coverage completed successfully"

# Fast testing with optimizations
test-fast: test-prep test-lint test-molecule-parallel
	@echo "Fast tests completed successfully"

test-prep: docker-build-base

# Build optimized Docker base image (only for local development)
docker-build-base:
	@if [ "$$CI" != "true" ] && [ "$$GITHUB_ACTIONS" != "true" ]; then \
		echo "Building optimized Docker base image for local testing..."; \
		cd roles/localhost/molecule && docker build -t ansible-home-test-base:latest -f Dockerfile.base . || echo "Docker build failed, falling back to standard images"; \
	else \
		echo "Skipping Docker build in CI/CD environment"; \
	fi

# Parallel test execution
test-molecule-parallel:
	@echo "Running Molecule scenarios in parallel..."
	@$(MAKE) molecule-test-default molecule-test-idempotence molecule-test-linux-fast --jobs=3 || \
	(echo "Parallel tests failed, falling back to sequential execution" && $(MAKE) test-molecule)

test-lint:
	@echo "Running pre-commit formatting checks..."
	poetry run pre-commit run --all-files
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

# Development workflow targets
dev-test: test-prep test-lint molecule-converge-all molecule-verify-all
	@echo "Development testing completed (containers preserved for reuse)"

dev-test-quick: test-lint molecule-verify-all
	@echo "Quick development test completed (reusing existing containers)"

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

molecule-test-linux-fast:
	cd roles/localhost && poetry run molecule test -s linux-fast

molecule-test-macos-utm:
	@echo "Running Molecule macOS tests with UTM VM..."
	./scripts/utm-macos-test.sh test

# Container reuse strategies for quick iterations
molecule-converge-all:
	@echo "Converging all scenarios (no destroy)..."
	@$(MAKE) molecule-converge-default molecule-converge-linux molecule-converge-linux-fast --jobs=3

molecule-converge-default:
	cd roles/localhost && poetry run molecule converge -s default

molecule-converge-linux:
	cd roles/localhost && poetry run molecule converge -s linux

molecule-converge-linux-fast:
	cd roles/localhost && poetry run molecule converge -s linux-fast

# Quick verify without full test cycle
molecule-verify-all:
	@echo "Verifying all scenarios (reuse containers)..."
	@$(MAKE) molecule-verify-default molecule-verify-linux molecule-verify-linux-fast --jobs=3

molecule-verify-default:
	cd roles/localhost && poetry run molecule verify -s default

molecule-verify-linux:
	cd roles/localhost && poetry run molecule verify -s linux

molecule-verify-linux-fast:
	cd roles/localhost && poetry run molecule verify -s linux-fast

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
