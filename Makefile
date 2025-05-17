dev-setup:
	poetry env remove --all || true
	rm -f .env
	python3 -m venv .venv
	poetry install
