test:
	@uv run pytest tests

lint:
	@uvx pre-commit run --all-files

install:
	@uv sync

build:
	@uv build
