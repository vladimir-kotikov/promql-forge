# Terminology:
# Selector - an expression that allows to select a subset of an another
# expression which is's applied to, e.g.:
#   - label selector {foo="bar"} - selects a subset of a metric/vector's time series
#   - range selector [5m] - selects a range vector from an instant vector
#   - subquery [5m:1m] - selects a range vector from an instant vector expression
#   - instant selector @ 1609459200 - selects a fixed instant from an instant
#     vector expression
#   - grouping selector by/without (foo) - selects grouping for an aggregation
#
# Modifier - an expression that modifies the behavior of an another expression, e.g.:
#   - offset 5m - modifies an instant vector to select data from a different time
#   - on/ignoring (foo) - modifies a binary vector expression to match on
#     specific labels
#   - group_left/group_right (foo) - modifies a binary vector expression to allow
#     one-to-many matching
#
# Metric - a named time series, an instant vector without any selectors/modifiers
#
# Instant vector - a set of time series at a specific time (e.g. metric with label
# selectors, range selector, instant selector, offset modifier)
#
# Instant vector expression - an expression that evaluates to an instant vector
# (e.g. instant vector, function, aggregation, binary vector expression)
#
# Range vector - a set of time series over a time range (e.g. instant vector
# with range selector, subquery applied or an instant vector expression with a
# subquery applied)
#
# Scalar - a single numerical value
#
# Scalar expression - an expression that evaluates to a scalar (e.g. scalar,
# binary scalar expression)

import re
from typing import Literal, Protocol, Unpack, runtime_checkable

from promql_builder.util import ToPromqlParams, promql_join, to_promql

type LabelOperator = Literal["=", "!=", "=~", "!~"]
type Duration = str | int | float | GrafanaVar
type BinaryArithmeticOperator = Literal["+", "-", "*", "/", "%", "^"]
type BinaryComparisonOperator = Literal[">", "<", ">=", "<=", "=", "!="]
type BinaryScalarOperator = BinaryArithmeticOperator | BinaryComparisonOperator
type BinaryVectorOperator = (
    BinaryArithmeticOperator | BinaryComparisonOperator | Literal["and", "or", "unless"]
)
type Scalar = float | int


range_re = re.compile(r"^[0-9]+(?:ms|s|m|h|d|w|y)$")


def validate_duration(range: Duration, allow_negative: bool = False) -> None:
    if isinstance(range, GrafanaVar):
        return

    if isinstance(range, str):
        if allow_negative and range[0] == "-":
            range = range[1:]

        if range_re.fullmatch(range):
            return

    if isinstance(range, int | float):
        if range > 0 or allow_negative:
            return

    raise ValueError(f"Invalid range: {range}")


@runtime_checkable
class PromQlElement(Protocol):
    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str: ...


class GrafanaVarMeta(type):
    """
    Allows creating GrafanaVar instances via attribute access, e.g. GrafanaVar.var_name
    """

    def __getattr__(cls, item: str) -> "GrafanaVar":
        return cls(item)


class GrafanaVar(PromQlElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        return f"${{{self.name}}}"

    def __str__(self) -> str:
        return self.to_promql()


class Label(PromQlElement):
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, value: object) -> "LabelSelector":
        if not isinstance(value, (str, GrafanaVar)):
            raise ValueError("Label value must be a string or Grafana variable")

        return LabelSelector(self, "=", value)

    def __ne__(self, value: object) -> "LabelSelector":
        if not isinstance(value, (str, GrafanaVar)):
            raise ValueError("Label value must be a string or Grafana variable")

        return LabelSelector(self, "!=", value)

    def matches(self, value: object) -> "LabelSelector":
        if not isinstance(value, (str, GrafanaVar)):
            raise ValueError("Label value must be a string or Grafana variable")

        return LabelSelector(self, "=~", value)

    def not_matches(self, value: object) -> "LabelSelector":
        if not isinstance(value, (str, GrafanaVar)):
            raise ValueError("Label value must be a string or Grafana variable")

        return LabelSelector(self, "!~", value)

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        return self.name


class LabelSelector(PromQlElement):
    label: Label
    op: LabelOperator
    value: str | GrafanaVar

    def __init__(
        self, label: Label, op: LabelOperator, value: str | GrafanaVar
    ) -> None:
        self.label = label
        self.op = op
        self.value = value

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        return f'{self.label.name}{self.op}"{to_promql(self.value, **kwargs)}"'


class LabelModifier(PromQlElement):
    name: str

    def __init_subclass__(cls, name: str) -> None:
        cls.name = name

    def __init__(self, *labels: Label | str) -> None:
        if not labels:
            raise ValueError(f"{self.name} modifier requires at least one label")

        self._labels = labels

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        labels_str = promql_join(self._labels, parens="()", **kwargs)
        return f"{self.name} {labels_str}"


class Subquery(PromQlElement):
    def __init__(self, window: Duration, resolution: Duration | None = None) -> None:
        self.window = window
        self.resolution = resolution

        validate_duration(self.window)
        if self.resolution is not None:
            validate_duration(self.resolution, allow_negative=True)

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        resolution_str = "" if self.resolution is None else str(self.resolution)
        return f"{self.window}:{resolution_str}"
