dev-setup:
	poetry env remove --all || true
	rm -rf .venv
	python3 -m venv .venv
	@if ! command -v poetry >/dev/null 2>&1; then \
		.venv/bin/pip install poetry; \
		.venv/bin/poetry install; \
	else \
		poetry install; \
	fi
