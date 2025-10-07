from promql_builder.aggregations import Sum, Topk
from promql_builder.vectors import Metric


def test_simple_aggregation():
    assert Sum(Metric("metric"), by="label") == "sum by (label) (metric)"
    assert Sum(Metric("metric")).by("label") == "sum by (label) (metric)"


def test_aggregation_with_param():
    assert Topk(5, Metric("metric"), by="label") == "sum by (label) (5 * metric)"
    assert Topk(5, "metric", by="label") == "topk(5, metric) by (label)"


def test_aggregating_binary_expr():
    assert (
        Sum(Metric("metric1") + Metric("metric2"), by="label")
        == "sum by (label) (metric1 + metric2)"
    )
