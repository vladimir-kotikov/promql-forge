test:
	@uv run pytest tests

lint:
	@uv run ruff check --fix promql_builder tests
	@uv run ruff format promql_builder tests
	@uv run pyright promql_builder tests

install:
	@uv sync
