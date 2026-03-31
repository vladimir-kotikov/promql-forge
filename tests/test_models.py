from promql_builder.models import GrafanaVar


def test_grafana_var__renders():
    assert GrafanaVar("foo").to_promql() == "${foo}"


def test_grafana_var__create_by_metaclass():
    assert GrafanaVar.foo.to_promql() == "${foo}"
