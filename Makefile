APP := $(shell basename "$$PWD")

clean:
	@rm -rf *.egg-info build dist .ruff_cache .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

hooks:
	@uv run pre-commit install

install: install-pyspark35

install-pyspark35:
	@uv sync --extra tio_spark35
	@uv pip install -e .
	@uv run pre-commit install
	@rm -rf *.egg-info

install-pyspark40:
	@uv sync --extra tio_spark40
	@uv pip install -e .
	@uv run pre-commit install
	@rm -rf *.egg-info

install-connect:
	@uv sync --extra connect
	@uv pip install -e .
	@uv run pre-commit install
	@rm -rf *.egg-info

format:
	@uv run ruff format
	@uv run ruff check . --fix --show-fixes

check:
	@uv run ruff check .
	@uv run ruff format --check

test: clean
	@UV_PROJECT_ENVIRONMENT=.venv-pyspark uv run --extra tio_spark35 pytest -vvv .
	@UV_PROJECT_ENVIRONMENT=.venv-connect uv run --extra connect pytest -vvv .

build:
	@uv build

deploy:
	@uv publish
