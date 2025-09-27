from typing import Literal

type Label = str
type LabelOperator = Literal["=", "!=", "=~", "!~"]
type Duration = str | Scalar | GrafanaVar
type BinaryArithmeticOperator = Literal["+", "-", "*", "/", "%", "^"]
type BinaryComparisonOperator = Literal[">", "<", ">=", "<=", "=", "!="]
type BinaryScalarOperator = BinaryArithmeticOperator | BinaryComparisonOperator
type BinaryVectorOperator = BinaryArithmeticOperator | BinaryComparisonOperator | Literal[
    "and", "or", "unless"
]
type Scalar = float | int
type RawMetric = str
type Arg = str | ScalarExpression | VectorExpression | RangeSelector
type VectorExpression = RawMetric | VectorSelector | Function | Aggregation | "BinaryVectorExpression"
type ScalarExpression = Scalar | "BinaryScalarExpression"
type Query = VectorExpression | VectorSelector | ScalarExpression


class GrafanaVar:
    name: str


class Range:
    window: Duration
    resolution: Duration | None


class LabelSelector:
    label: Label
    op: LabelOperator
    value: str | GrafanaVar


class VectorSelector:
    expression: RawMetric
    selectors: tuple[LabelSelector, ...] | None
    offset: Duration | None
    at: int | float | None


class RangeSelector:
    expression: VectorExpression
    range: Range


class Function:
    name: str
    args: tuple[Arg, ...]


class Aggregation:
    name: str
    expression: VectorExpression
    arg: Arg | None
    by: tuple[Label, ...] | None
    without: tuple[Label, ...] | None


class BinaryVectorExpression:
    left: VectorExpression
    right: VectorExpression | ScalarExpression
    operator: BinaryVectorOperator
    on: tuple[Label, ...] | None
    ignoring: tuple[Label, ...] | None
    group_left: tuple[Label, ...] | None
    group_right: tuple[Label, ...] | None


class BinaryScalarExpression:
    left: ScalarExpression
    right: ScalarExpression
    operator: BinaryScalarOperator
