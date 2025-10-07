from typing import overload

from promql_builder.expressions import Aggregation
from promql_builder.models import GrafanaVar, Label
from promql_builder.modifiers import AggregationModifier, By, Without
from promql_builder.vectors import InstantVector

type IntParam = int | GrafanaVar
type NumericParam = int | float | GrafanaVar
type LabelGroupSelector = str | Label
type LabelGroupSelectors = LabelGroupSelector | tuple[LabelGroupSelector, ...]
type InstantVectorExpression = InstantVector | str


def to_aggregation_modifier(
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> AggregationModifier | None:
    if by and without:
        raise ValueError("Cannot specify both 'by' and 'without' for aggregation")

    if by:
        if isinstance(by, tuple):
            return By(*by)
        else:
            return By(by)

    if without:
        if isinstance(without, tuple):
            return Without(*without)
        else:
            return Without(without)

    return None


@overload
def Sum(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Sum(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Sum(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "sum", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Avg(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Avg(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Avg(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "avg", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Min(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Min(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Min(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "min", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Max(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Max(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Max(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "max", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Group(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Group(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Group(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "group", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Count(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Count(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Count(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "count", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Stddev(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Stddev(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Stddev(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "stddev", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Stdvar(
    vector: InstantVectorExpression, *, by: LabelGroupSelectors | None = None
) -> Aggregation: ...
@overload
def Stdvar(
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Stdvar(
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "stdvar", vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Topk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
) -> Aggregation: ...
@overload
def Topk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Topk(
    k: IntParam,
    vector: InstantVectorExpression,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "topk", k, vector, group=to_aggregation_modifier(by=by, without=without)
    )


@overload
def Bottomk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
) -> Aggregation: ...
@overload
def Bottomk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Bottomk(
    k: IntParam,
    vector: InstantVectorExpression,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "bottomk",
        k,
        vector,
        group=to_aggregation_modifier(by=by, without=without),
    )


@overload
def Limitk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
) -> Aggregation: ...
@overload
def Limitk(
    k: IntParam,
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Limitk(
    k: IntParam,
    vector: InstantVectorExpression,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "limitk",
        k,
        vector,
        group=to_aggregation_modifier(by=by, without=without),
    )


@overload
def CountValues(
    val: NumericParam,
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
) -> Aggregation: ...
@overload
def CountValues(
    val: NumericParam,
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def CountValues(
    val: NumericParam,
    vector: InstantVectorExpression,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    return Aggregation(
        "count_values",
        val,
        vector,
        to_aggregation_modifier(by=by, without=without),
    )


@overload
def Quantile(
    phi: NumericParam,
    vector: InstantVectorExpression,
    *,
    by: LabelGroupSelectors | None = None,
) -> Aggregation: ...
@overload
def Quantile(
    phi: NumericParam,
    vector: InstantVectorExpression,
    *,
    without: LabelGroupSelectors | None = None,
) -> Aggregation: ...
def Quantile(
    phi: NumericParam,
    vector: InstantVectorExpression,
    by: LabelGroupSelectors | None = None,
    without: LabelGroupSelectors | None = None,
) -> Aggregation:
    if isinstance(phi, int | float) and not (0 <= phi <= 1):
        raise ValueError("Quantile phi must be between 0 and 1")

    return Aggregation(
        "quantile",
        phi,
        vector,
        group=to_aggregation_modifier(by=by, without=without),
    )
