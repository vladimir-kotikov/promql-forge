from textwrap import dedent

import pytest

from promql_forge.functions import Delta
from promql_forge.models import GrafanaVar
from promql_forge.vectors import Metric


def test_simple_metric():
    assert str(Metric("my_fancy_metic")) == "my_fancy_metic"


def test_metric_with_simple_labels():
    query = Metric("my_other_metric").labels(foo="bar", baz="quux")

    assert query.to_promql(compact=True) == 'my_other_metric{foo="bar",baz="quux"}'
    assert str(query) == dedent("""\
        my_other_metric{
            foo="bar",
            baz="quux"
        }""")


def test_metric_with_labels_as_properties():
    metric = Metric("my_other_metric")
    query = metric.labels(
        metric.foo == "bar",
        metric.baz != "quux",
        metric.env.matches("prod"),
        metric.version.not_matches("v1.*"),
    )

    assert (
        query.to_promql(compact=True)
        == 'my_other_metric{foo="bar",baz!="quux",env=~"prod",version!~"v1.*"}'
    )
    assert str(query) == dedent("""\
            my_other_metric{
                foo="bar",
                baz!="quux",
                env=~"prod",
                version!~"v1.*"
            }""")


def test_metric_with_variables_labels():
    metric = Metric("my_other_metric")
    query = metric.labels(
        metric.baz != GrafanaVar("quux"),
        metric.env.matches(f"{GrafanaVar('env')}.env"),
        foo=GrafanaVar("bar"),
    )

    assert (
        query.to_promql(compact=True)
        == 'my_other_metric{baz!="${quux}",env=~"${env}.env",foo="${bar}"}'
    )

    assert str(query) == dedent("""\
        my_other_metric{
            baz!="${quux}",
            env=~"${env}.env",
            foo="${bar}"
        }""")


@pytest.mark.parametrize("expression", ["foo", Metric("foo")])
def test_simple_function(expression):
    assert str(Delta(expression)) == "delta(foo)"


@pytest.mark.parametrize("offset", ["5m", 300, "-5m"])
def test_instant_vector__with_offset(offset):
    vec = Metric("foo").labels(foo="bar").offset(offset)

    assert str(vec) == f'foo{{foo="bar"}} offset {offset}'


def test_instant_vector__with_range():
    assert str(Metric("foo").over("10m")) == "foo[10m]"
    assert str(Metric("foo")["10m"]) == "foo[10m]"


def test_instant_vector__over_invalid_duration_raises():
    with pytest.raises(ValueError):
        Metric("foo").over("not_a_duration")


def test_metric_at_timestamp():
    assert str(Metric("foo").at(1234567890)) == "foo @ 1234567890"
    assert str(Metric("foo") @ 1234567890) == "foo @ 1234567890"


def test_metric_at_start_end():
    assert str(Metric("foo").at("start")) == "foo @ start()"
    assert str(Metric("foo").at("end")) == "foo @ end()"


def test_metric_at_duplicate_raises():
    with pytest.raises(ValueError):
        Metric("foo").at(100).at(200)


def test_metric_offset_duplicate_raises():
    with pytest.raises(ValueError):
        Metric("foo").offset("5m").offset("10m")
