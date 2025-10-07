import pytest

from promql_builder.functions import Delta
from promql_builder.models import GrafanaVar
from promql_builder.vectors import Metric


def test_simple_metric():
    assert str(Metric("my_fancy_metic")) == "my_fancy_metic"


def test_metric_with_simple_labels():
    query = Metric("my_other_metric").labels(foo="bar", baz="quux")

    assert str(query) == 'my_other_metric{foo="bar", baz="quux"}'


def test_metric_with_labels_as_properties():
    metric = Metric("my_other_metric")
    query = metric.labels(
        metric.foo == "bar",
        metric.baz != "quux",
        metric.env.matches("prod"),
        metric.version.not_matches("v1.*"),
    )

    assert (
        str(query)
        == 'my_other_metric{foo="bar", baz!="quux", env=~"prod", version!~"v1.*"}'
    )


def test_metric_with_variables_labels():
    metric = Metric("my_other_metric")
    query = metric.labels(
        metric.baz != GrafanaVar("quux"),
        metric.env.matches(f"{GrafanaVar('env')}.env"),
        foo=GrafanaVar("bar"),
    )

    assert (
        str(query) == 'my_other_metric{baz!="${quux}", env=~"${env}.env", foo="${bar}"}'
    )


@pytest.mark.parametrize(
    "expression",
    [
        "foo",
        Metric("foo"),
        Metric("foo"),
    ],
)
def test_simple_function(expression):
    assert str(Delta(expression)) == "delta(foo)"


@pytest.mark.parametrize("offset", ["5m", 300, "-5m"])
def test_instant_vector__with_offset(offset):
    vec = Metric("foo").labels(foo="bar").offset(offset)

    assert str(vec) == f'foo{{foo="bar"}} offset {offset}'


def test_instant_vector__with_range():
    assert str(Metric("foo").over("10m")) == "foo[10m]"
    assert str(Metric("foo")["10m"]) == "foo[10m]"
