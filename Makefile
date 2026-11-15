APP := $(shell basename "$$PWD")

clean:
	@rm -rf *.egg-info build dist .ruff_cache .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

hooks:
	@uv run pre-commit install

install:
	@rm -rf .venv
	@uv sync
	@uv pip install -e .

install-dev:
	@rm -rf .venv
	@uv sync --group pyspark
	@uv pip install -e .
	@uv run pre-commit install
	@rm -rf *.egg-info

install-pyspark:
	@rm -rf .venv
	@uv sync --group pyspark

install-connect:
	@rm -rf .venv
	@uv sync --group connect

format:
	@uv run ruff format
	@uv run ruff check . --fix --show-fixes

check:
	@uv run ruff check .
	@uv run ruff format --check

test: clean
	@UV_PROJECT_ENVIRONMENT=.venv-pyspark uv run --group pyspark pytest -vvv .
	@UV_PROJECT_ENVIRONMENT=.venv-connect uv run --group connect pytest -vvv .

build:
	@uv build

deploy:
	@uv publish
