from typing import Any


def to_promql(expr: Any, quote_strings: bool = False) -> str:
    if hasattr(expr, "to_promql"):
        return expr.to_promql()

    if isinstance(expr, str):
        if quote_strings:
            return f'"{expr}"'

        return expr

    return str(expr)


def quote(expr: Any, quote_char: str = '"') -> Any:
    if isinstance(expr, str):
        return f"{quote_char}{expr}{quote_char}"
    return expr
