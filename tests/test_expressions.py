import pytest

from promql_forge.functions import HistogramFraction, HistogramQuantile
from promql_forge.models import Subquery
from promql_forge.vectors import Metric
from tests.helpers import assert_promql


def test_subquery_with_resolution():
    sq = Subquery("5m", "1m")
    assert sq.to_promql(compact=True) == "5m:1m"


def test_subquery_without_resolution():
    sq = Subquery("5m")
    assert sq.to_promql(compact=True) == "5m:"


def test_subquery_invalid_window_raises():
    with pytest.raises(ValueError):
        Subquery("not_a_duration")


def test_subquery_invalid_resolution_raises():
    with pytest.raises(ValueError):
        Subquery("5m", "bad")


def test_histogram_fraction_arg_order():
    assert_promql(
        HistogramFraction(0.1, 0.9, Metric("m")),
        "histogram_fraction(0.1,0.9,m)",
        compact=True,
    )


def test_histogram_quantile_arg_order():
    assert_promql(
        HistogramQuantile(0.95, Metric("m")),
        "histogram_quantile(0.95,m)",
        compact=True,
    )


def test_histogram_quantile_invalid_phi_raises():
    with pytest.raises(ValueError):
        HistogramQuantile(1.5, Metric("m"))


@pytest.mark.parametrize("compact", [True, False])
def test_binary_expr_on_empty_labels(compact):
    expr = (Metric("a") * Metric("b")).on()
    assert_promql(expr, "a * on() b", compact=compact)


@pytest.mark.parametrize("compact", [True, False])
def test_binary_expr_group_left_empty_labels(compact):
    assert_promql(
        (Metric("a") * Metric("b")).on("ns").group_left(),
        "a * on(ns) group_left() b",
        compact=compact,
    )


def test_binary_expr_on():
    expr = (Metric("a") + Metric("b")).on("ns", "pod")
    assert_promql(expr, "a + on(ns, pod) b", compact=False)
    assert_promql(expr, "a + on(ns,pod) b", compact=True)


@pytest.mark.parametrize("compact", [True, False])
def test_binary_expr_ignoring(compact):
    expr = (Metric("a") + Metric("b")).ignoring("env")
    assert_promql(expr, "a + ignoring(env) b", compact=compact)


@pytest.mark.parametrize("compact", [True, False])
def test_binary_expr_group_left(compact):
    assert_promql(
        (Metric("a") * Metric("b")).on("ns").group_left("extra"),
        "a * on(ns) group_left(extra) b",
        compact=compact,
    )


@pytest.mark.parametrize("compact", [True, False])
def test_binary_expr_group_right(compact):
    assert_promql(
        (Metric("a") * Metric("b")).on("ns").group_right("extra"),
        "a * on(ns) group_right(extra) b",
        compact=compact,
    )


def test_binary_expr_double_on_raises():
    with pytest.raises(ValueError):
        (Metric("a") + Metric("b")).on("ns").on("pod")


def test_binary_expr_double_group_raises():
    with pytest.raises(ValueError):
        (Metric("a") * Metric("b")).on("ns").group_left().group_right()
