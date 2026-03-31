from promql_builder.models import PromQlElement


def assert_promql(expr: PromQlElement, expected: str, **kwargs) -> None:
    """Assert that `expr` renders to the expected PromQL string.

    Use this instead of `expr == "..."` — the equality operator on vector
    expressions returns a BinaryVectorExpression (SQLAlchemy-style predicate),
    so direct `assert expr == "..."` always passes trivially.
    """
    assert expr.to_promql(**kwargs) == expected, (
        f"\nExpected: {expected!r}\n  Actual: {expr.to_promql(**kwargs)!r}"
    )
