import pytest

from promql_builder.aggregations import (
    Avg,
    Bottomk,
    CountValues,
    Group,
    Min,
    Quantile,
    Stddev,
    Stdvar,
    Sum,
    Topk,
)
from promql_builder.vectors import Metric
from tests.helpers import assert_promql


def test_simple_aggregation():
    assert_promql(
        Sum(Metric("metric"), by="label"),
        "sum(metric) by (label)",
        compact=False,
    )
    assert_promql(
        Sum(Metric("metric")).by("label"),
        "sum(metric) by(label)",
        compact=True,
    )


def test_aggregation_without():
    assert_promql(
        Sum(Metric("m"), without="label"),
        "sum(m) without (label)",
        compact=False,
    )
    assert_promql(
        Sum(Metric("m")).without("label"),
        "sum(m) without(label)",
        compact=True,
    )


def test_aggregation_multi_label_by():
    assert_promql(
        Sum(Metric("m"), by=("a", "b")),
        "sum(m) by(a,b)",
        compact=True,
    )


def test_aggregation_with_param():
    assert_promql(
        Topk(5, Metric("metric"), by="label"),
        "topk(5, metric) by (label)",
        compact=False,
    )
    assert_promql(
        Topk(5, "metric", by="label"),
        "topk(5,metric) by(label)",
        compact=True,
    )


def test_aggregating_binary_expr():
    assert_promql(
        Sum(Metric("metric1") + Metric("metric2"), by="label"),
        "sum(metric1 + metric2) by(label)",
        compact=True,
    )


def test_aggregation_modifier_first():
    assert_promql(
        Sum(Metric("metric"), by="label"),
        "sum by(label) (metric)",
        compact=True,
        modifier_first=True,
    )


def test_aggregation_modifier_first_without():
    assert_promql(
        Sum(Metric("m"), without=("a", "b")),
        "sum without(a,b) (m)",
        compact=True,
        modifier_first=True,
    )


def test_avg():
    assert_promql(
        Avg(Metric("m"), by="l"),
        "avg(m) by(l)",
        compact=True,
    )


def test_min():
    assert_promql(
        Min(Metric("m"), without="l"),
        "min(m) without(l)",
        compact=True,
    )


def test_bottomk():
    assert_promql(
        Bottomk(3, Metric("m")),
        "bottomk(3, m)",
        compact=False,
    )
    assert_promql(
        Bottomk(3, Metric("m"), by="l"),
        "bottomk(3,m) by(l)",
        compact=True,
    )


def test_count_values():
    assert_promql(
        CountValues("status", Metric("m")),
        'count_values("status",m)',
        compact=True,
    )


def test_count_values_with_group():
    assert_promql(
        CountValues("status", Metric("m"), by="l"),
        'count_values("status",m) by(l)',
        compact=True,
    )


def test_stddev():
    assert_promql(Stddev(Metric("m")), "stddev(m)", compact=True)
    assert_promql(
        Stddev(Metric("m"), by="l"),
        "stddev(m) by(l)",
        compact=True,
    )


def test_stdvar():
    assert_promql(
        Stdvar(Metric("m")),
        "stdvar(m)",
        compact=True,
    )


def test_group():
    assert_promql(
        Group(Metric("m"), by="l"),
        "group(m) by(l)",
        compact=True,
    )


def test_quantile():
    assert_promql(
        Quantile(0.95, Metric("m")),
        "quantile(0.95,m)",
        compact=True,
    )
    assert_promql(
        Quantile(0.95, Metric("m"), by="l"),
        "quantile(0.95, m) by (l)",
        compact=False,
    )


def test_quantile_invalid_phi():
    with pytest.raises(ValueError):
        Quantile(1.5, Metric("m"))
    with pytest.raises(ValueError):
        Quantile(-0.1, Metric("m"))


def test_double_grouping_raises():
    with pytest.raises(ValueError):
        Sum(Metric("m"), by="l").by("other")
