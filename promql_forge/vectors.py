import itertools
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Unpack, cast

from promql_forge.models import (
    BinaryVectorOperator,
    Duration,
    GrafanaVar,
    Label,
    LabelSelector,
    PromQlElement,
    Scalar,
    Subquery,
    ToPromqlParams,
    validate_duration,
)
from promql_forge.util import parenthesize, promql_join, to_promql

if TYPE_CHECKING:
    from promql_forge.expressions import (
        BinaryScalarExpression,
        BinaryVectorExpression,
    )


type InstantVectorExpression = InstantVector | str
type ScalarExpression = Scalar | BinaryScalarExpression
type AnyExpression = InstantVectorExpression | ScalarExpression


class VectorBinaryOperationsMixin:
    def _op(
        self,
        other: AnyExpression,
        operator: BinaryVectorOperator,
    ) -> "BinaryVectorExpression":
        from promql_forge.expressions import BinaryVectorExpression

        return BinaryVectorExpression(
            left=cast(InstantVectorExpression, self),
            operator=operator,
            right=other,
        )

    # Arithmetics
    def __add__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "+")

    def __sub__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "-")

    def __mul__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "*")

    def __truediv__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "/")

    def __mod__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "%")

    def __pow__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "^")

    # Comparisons
    def __gt__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, ">")

    def __lt__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "<")

    def __ge__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, ">=")

    def __le__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "<=")

    def __eq__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "=")

    def __ne__(self, other: AnyExpression) -> "BinaryVectorExpression":
        return self._op(other, "!=")

    # Logical
    def __and__(self, other: InstantVectorExpression) -> "BinaryVectorExpression":
        return self._op(other, "and")

    def __or__(self, other: InstantVectorExpression) -> "BinaryVectorExpression":
        return self._op(other, "or")

    def and_(self, other: InstantVectorExpression) -> "BinaryVectorExpression":
        return self & other

    def or_(self, other: InstantVectorExpression) -> "BinaryVectorExpression":
        return self | other

    def unless(self, other: InstantVectorExpression) -> "BinaryVectorExpression":
        return self._op(other, "unless")


class InstantVector(ABC, VectorBinaryOperationsMixin):
    def subquery(self, subquery: Duration | Subquery | slice) -> "RangeVector":
        if isinstance(subquery, Subquery):
            pass
        elif isinstance(subquery, slice):
            if subquery.step is not None:
                raise ValueError("Subquery step is not supported")

            subquery = Subquery(subquery.start, subquery.stop)
        else:
            subquery = Subquery(subquery)

        return RangeVector(self, subquery)

    def over(self, subquery: Duration | Subquery | slice) -> "RangeVector":
        return self.subquery(subquery)

    def __getitem__(self, subquery: Duration | Subquery | slice) -> "RangeVector":
        return self.subquery(subquery)


class Metric(InstantVector):
    def __init__(
        self,
        name: str,
        labels: tuple[LabelSelector, ...] = tuple(),
        /,
        offset: Duration | None = None,
        instant: int | float | Literal["start", "end"] | None = None,
    ):
        self._name = name
        self._labels = labels
        self._offset = offset
        self._instant: int | float | None | Literal["start"] | Literal["end"] = instant

    def labels(
        self, *selectors: LabelSelector, **kwlabels: str | GrafanaVar
    ) -> "Metric":
        kw_selectors = [Label(k) == v for k, v in kwlabels.items()]

        return Metric(
            self._name,
            tuple(itertools.chain(self._labels, selectors, kw_selectors)),
            offset=self._offset,
            instant=self._instant,
        )

    def over(self, range: Duration) -> "RangeVector":
        validate_duration(range)
        return RangeVector(self, range)

    def offset(self, duration: Duration) -> "Metric":
        if self._offset is not None:
            raise ValueError("Offset is already set")

        return Metric(self._name, self._labels, offset=duration, instant=self._instant)

    def at(self, timestamp: int | float | Literal["start", "end"]) -> "Metric":
        if self._instant is not None:
            raise ValueError("Instant is already set")

        return Metric(self._name, self._labels, offset=self._offset, instant=timestamp)

    def __matmul__(self, timestamp: int | float | Literal["start", "end"]) -> "Metric":
        return self.at(timestamp)

    def __getitem__(self, range: Duration) -> "RangeVector":
        return self.over(range)

    def __getattr__(self, name: str) -> Label:
        return Label(name)

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        promql = self._name
        if self._labels:
            promql += promql_join(self._labels, parens="{}", **kwargs)

        if self._offset is not None:
            promql += f" offset {to_promql(self._offset)}"

        if self._instant is not None:
            instant_str = str(self._instant)
            if self._instant in ["start", "end"]:
                instant_str = f"{self._instant}()"

            promql += f" @ {instant_str}"

        return promql

    def __str__(self) -> str:
        return self.to_promql()


@dataclass
class RangeVector(PromQlElement):
    expression: InstantVector
    range: Duration | Subquery

    def to_promql(self, **kwargs: Unpack[ToPromqlParams]) -> str:
        expr_str = to_promql(self.expression, **kwargs)
        if not isinstance(self.expression, str | Metric):
            expr_str = parenthesize(expr_str, **kwargs)

        return f"{expr_str}[{to_promql(self.range, **kwargs)}]"

    def __str__(self) -> str:
        return self.to_promql()
