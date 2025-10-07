test:
	@uv run pytest tests

lint:
	@uvx ruff format promql_builder tests
	@uvx ruff check --fix promql_builder tests
	@uvx pyright promql_builder tests

install:
	@uv sync
