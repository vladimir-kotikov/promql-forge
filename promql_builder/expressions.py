from dataclasses import dataclass
from typing import Any, Literal, Unpack

from promql_builder.models import Label, PromQlElement, ToPromqlParams
from promql_builder.modifiers import (
    AggregationModifier,
    By,
    ExpressionGroupModifier,
    ExpressionLabelsModifier,
    GroupLeft,
    GroupRight,
    Ignoring,
    On,
    Without,
)
from promql_builder.util import (
    DEFAULT_NO_WRAP_LIMIT,
    parenthesize,
    promql_join,
    to_promql,
)
from promql_builder.vectors import InstantVector

type LabelGroupSelector = str | Label
type BinaryArithmeticOperator = Literal["+", "-", "*", "/", "%", "^"]
type BinaryComparisonOperator = Literal[">", "<", ">=", "<=", "=", "!="]
type BinaryScalarOperator = BinaryArithmeticOperator | BinaryComparisonOperator
type BinaryVectorOperator = (
    BinaryArithmeticOperator | BinaryComparisonOperator | Literal["and", "or", "unless"]
)
type Scalar = float | int
type ScalarExpression = Scalar | BinaryScalarExpression
type InstantVectorExpression = InstantVector | str


@dataclass
class BinaryScalarExpression:
    left: ScalarExpression
    right: ScalarExpression
    operator: BinaryScalarOperator

    def to_promql(self) -> str:
        return f"{to_promql(self.left)} {self.operator} {to_promql(self.right)}"


class BinaryVectorExpression(InstantVector, PromQlElement):
    def __init__(
        self,
        left: InstantVectorExpression,
        operator: BinaryVectorOperator,
        right: InstantVectorExpression | ScalarExpression,
        *,
        labels: ExpressionLabelsModifier | None = None,
        group: ExpressionGroupModifier | None = None,
    ) -> None:
        self._left: InstantVectorExpression = left
        self._operator: BinaryVectorOperator = operator
        self._right: InstantVectorExpression | ScalarExpression = right
        self._labels = labels
        self._group = group

    def _copy(self, **updated: Any) -> "BinaryVectorExpression":
        for _mod in ("on", "ignoring"):
            if _mod in updated and self._labels is not None:
                raise ValueError(
                    f"Cannot use '{_mod}' on an expression that "
                    "has labels already defined"
                )

        for _mod in ("group_left", "group_right"):
            if _mod in updated and self._group is not None:
                raise ValueError(
                    f"Cannot use '{_mod}' on an expression that "
                    "has group modifier already defined"
                )

        kwargs = {
            "left": self._left,
            "operator": self._operator,
            "right": self._right,
            "labels": self._labels,
            "group": self._group,
        }
        kwargs.update(updated)

        return BinaryVectorExpression(**kwargs)

    def on(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(labels=On(*labels))

    def ignoring(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(labels=Ignoring(*labels))

    def group_left(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(group=GroupLeft(*labels))

    def group_right(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(group=GroupRight(*labels))

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        compact = kwargs.get("compact", False)

        left_str = to_promql(self._left, **kwargs)
        if isinstance(self._left, BinaryVectorExpression):
            left_str = parenthesize(left_str, **kwargs)

        right_str = to_promql(self._right, **kwargs)
        if isinstance(self._right, BinaryVectorExpression):
            right_str = parenthesize(right_str, **kwargs)

        op_str = self._operator
        if self._labels:
            op_str += " " + self._labels.to_promql(**kwargs)

        if self._group:
            op_str += " " + self._group.to_promql(**kwargs)

        joiner = "\n"
        if (
            compact
            or len(left_str) < DEFAULT_NO_WRAP_LIMIT
            or len(right_str) < DEFAULT_NO_WRAP_LIMIT
        ):
            joiner = " "

        return joiner.join([left_str, op_str, right_str])

    def __str__(self) -> str:
        return self.to_promql()


class Aggregation(InstantVector, PromQlElement):
    def __init__(
        self,
        name: str,
        *args: Any,
        group: AggregationModifier | None = None,
    ) -> None:
        self.name = name
        self._args = args
        self._group = group

    def _copy(self, group: AggregationModifier) -> "Aggregation":
        if self._group:
            raise ValueError("Cannot group an aggregation that already has grouping")

        return Aggregation(self.name, *self._args, group=group)

    def by(self, *labels: LabelGroupSelector) -> "Aggregation":
        return self._copy(By(*labels))

    def without(self, *labels: LabelGroupSelector) -> "Aggregation":
        return self._copy(Without(*labels))

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        args_str = promql_join(self._args, parens="()", **kwargs)
        result = f"{self.name}{args_str}"

        if self._group:
            result += " " + self._group.to_promql(**kwargs)

        return result

    def __str__(self) -> str:
        return self.to_promql()


class Function(InstantVector, PromQlElement):
    def __init__(self, name: str, *args: Any) -> None:
        self.name = name
        self.args = args

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        args_str = promql_join(self.args, parens="()", **kwargs)
        return f"{self.name}{args_str}"

    def __str__(self) -> str:
        return self.to_promql()
