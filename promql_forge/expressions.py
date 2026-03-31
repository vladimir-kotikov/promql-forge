from dataclasses import dataclass
from typing import Any, Unpack

from promql_forge.models import (
    BinaryScalarOperator,
    BinaryVectorOperator,
    Label,
    LabelModifier,
    PromQlElement,
    Scalar,
    ToPromqlParams,
)
from promql_forge.util import (
    DEFAULT_NO_WRAP_LIMIT,
    parenthesize,
    promql_join,
    to_promql,
)
from promql_forge.vectors import InstantVector

type LabelGroupSelector = str | Label
type ScalarExpression = Scalar | BinaryScalarExpression
type InstantVectorExpression = InstantVector | str
type AggregationModifier = By | Without
type ExpressionMatchModifier = On | Ignoring
type ExpressionGroupModifier = GroupLeft | GroupRight


class By(LabelModifier, name="by"): ...


class Without(LabelModifier, name="without"): ...


class On(
    LabelModifier,
    name="on",
    no_whitespace_before_parens=True,
): ...


class Ignoring(
    LabelModifier,
    name="ignoring",
    no_whitespace_before_parens=True,
): ...


class GroupLeft(
    LabelModifier,
    name="group_left",
    no_whitespace_before_parens=True,
): ...


class GroupRight(
    LabelModifier,
    name="group_right",
    no_whitespace_before_parens=True,
): ...


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
        match: ExpressionMatchModifier | None = None,
        group: ExpressionGroupModifier | None = None,
    ) -> None:
        self._left: InstantVectorExpression = left
        self._operator: BinaryVectorOperator = operator
        self._right: InstantVectorExpression | ScalarExpression = right
        self._match = match
        self._group = group

    def _copy(self, **updated: Any) -> "BinaryVectorExpression":
        if "match" in updated and self._match is not None:
            raise ValueError(
                "Cannot set label matching on an expression that "
                "already has label matching defined"
            )

        if "group" in updated and self._group is not None:
            raise ValueError(
                "Cannot set group modifier on an expression that "
                "already has a group modifier defined"
            )

        kwargs = {
            "left": self._left,
            "operator": self._operator,
            "right": self._right,
            "match": self._match,
            "group": self._group,
        }
        kwargs.update(updated)

        return BinaryVectorExpression(**kwargs)

    def on(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(match=On(*labels))

    def ignoring(self, *labels: Label | str) -> "BinaryVectorExpression":
        return self._copy(match=Ignoring(*labels))

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
        if self._match:
            op_str += " " + self._match.to_promql(**kwargs)

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
        aggregate: AggregationModifier | None = None,
    ) -> None:
        self.name = name
        self._args = args
        self._aggregate = aggregate

    def _copy(self, aggregate: AggregationModifier) -> "Aggregation":
        if self._aggregate:
            raise ValueError("Cannot group an aggregation that already has grouping")

        return Aggregation(self.name, *self._args, aggregate=aggregate)

    def by(self, *labels: LabelGroupSelector) -> "Aggregation":
        return self._copy(By(*labels))

    def without(self, *labels: LabelGroupSelector) -> "Aggregation":
        return self._copy(Without(*labels))

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        modifier_first = kwargs.get("modifier_first", False)
        args_str = promql_join(self._args, parens="()", **kwargs)

        if self._aggregate:
            group_str = self._aggregate.to_promql(**kwargs)
            if modifier_first:
                return f"{self.name} {group_str} {args_str}"
            else:
                return f"{self.name}{args_str} {group_str}"

        return f"{self.name}{args_str}"

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
