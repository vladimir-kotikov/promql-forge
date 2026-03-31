import textwrap
from typing import Any, Iterable, TypedDict, Unpack

DEFAULT_INDENT = 4
DEFAULT_NO_WRAP_LIMIT = 15


class ToPromqlParams(TypedDict, total=False):
    compact: bool
    indent: int
    no_wrap: bool
    modifier_first: bool


def to_promql(expr: Any, **kwargs: Unpack[ToPromqlParams]) -> str:
    from promql_forge.models import PromQlElement

    if isinstance(expr, PromQlElement):
        return expr.to_promql(**kwargs)

    if isinstance(expr, str):
        return expr

    return str(expr)


def quote(expr: Any, quote_char: str = '"') -> Any:
    if isinstance(expr, str):
        return f"{quote_char}{expr}{quote_char}"
    return expr


def promql_join(
    items: Iterable[Any],
    parens: str = "",
    **kwargs: Unpack[ToPromqlParams],
) -> str:
    str_items = [to_promql(item, **kwargs) for item in items]

    compact = kwargs.get("compact")
    # For short lists, use a more compact representation
    no_wrap = sum(len(s) for s in str_items) <= DEFAULT_NO_WRAP_LIMIT or kwargs.get(
        "no_wrap", False
    )
    joiner = "," if compact else ",\n"
    if no_wrap and not compact:
        joiner = ", "

    joined = joiner.join(str_items)
    if parens:
        joined = parenthesize(
            joined,
            parens,
            **{**kwargs, "compact": compact or no_wrap},
        )

    return joined


def parenthesize(
    expr: str,
    parens: str = "()",
    **kwargs: Unpack[ToPromqlParams],
) -> str:
    if len(parens) % 2 != 0:
        raise ValueError("parens must be a string of pair characters")

    n = len(parens) // 2
    left, right = parens[:n], parens[-n:]

    if kwargs.get("compact"):
        return f"{left}{expr}{right}"

    indented = textwrap.indent(expr, " " * kwargs.get("indent", DEFAULT_INDENT))
    return f"{left}\n{indented}\n{right}"
