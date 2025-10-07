from promql_builder.aggregations import Count, Max, Sum
from promql_builder.functions import Changes, Increase, LabelReplace, Vector
from promql_builder.models import GrafanaVar, Label
from promql_builder.vectors import Metric


def compact(s: str, sub: str = ":") -> str:
    old, new = sub.split(":", maxsplit=1)
    return "".join(line.strip().replace(old, new) for line in s.strip().splitlines())


def test_sumby_count_le() -> None:
    containers_running = Metric("kube_pod_container_status_running")

    base = containers_running.labels(
        Label("namespace").matches(GrafanaVar("namespace")),
        Label("owner").matches(GrafanaVar("cluster")),
    )

    _sum = Sum(base).by("pod") >= 1
    query = Count(_sum)

    assert (
        str(query)
        == 'count(sum(kube_pod_container_status_running{namespace=~"${namespace}",'
        ' owner=~"${cluster}"}) by (pod) >= 1)'
    )


def test_sum_increase() -> None:
    query = Sum(
        Increase(
            Metric("kube_pod_container_status_restarts_total").labels(
                Label("owner").matches(GrafanaVar("cluster")),
                Label("namespace").matches(GrafanaVar("namespace")),
            )[GrafanaVar("__range")]
        )
    )

    assert (
        str(query) == "sum(increase(kube_pod_container_status_restarts_total"
        '{owner=~"${cluster}", namespace=~"${namespace}"}[${__range}]))'
    )


def test_sum_or_vector() -> None:
    kube_cronjob_status = Metric("kube_cronjob_status_active").labels(
        Label("namespace").matches(GrafanaVar("namespace"))
    )

    query = Sum(kube_cronjob_status) | Vector(0)

    assert (
        str(query)
        == 'sum(kube_cronjob_status_active{namespace=~"${namespace}"}) or vector(0)'
    )


def test_count_or_vector() -> None:
    query = Count(
        Metric("kube_cronjob_status_active").labels(
            Label("owner").matches(GrafanaVar("cluster")),
            Label("namespace").matches(GrafanaVar("namespace")),
        )
    ) | Vector(0)

    assert (
        str(query) == 'count(kube_cronjob_status_active{owner=~"${cluster}", '
        'namespace=~"${namespace}"}) or vector(0)'
    )


def test_sum_multiply_divide() -> None:
    cpu_requests = Metric("kube_pod_container_resource_requests")
    cpu_capacity = Metric("kube_node_status_capacity")

    sum_requests = (
        Sum(cpu_requests.labels(owner=GrafanaVar("cluster"), resource="cpu")) * 100
    )

    sum_capacity = Sum(cpu_capacity.labels(owner=GrafanaVar("cluster"), resource="cpu"))

    query = sum_requests / sum_capacity

    assert (
        str(query) == '(sum(kube_pod_container_resource_requests{owner="${cluster}",'
        ' resource="cpu"}) * 100) /'
        ' sum(kube_node_status_capacity{owner="${cluster}", resource="cpu"})'
    )


def test_max_by_multiple_divide_label_replace() -> None:
    docker_cpu = Metric("docker_container_cpu_usage_percent")
    kube_limits = Metric("kube_pod_container_resource_limits")

    max_docker = (
        Max(
            docker_cpu.labels(
                owner=GrafanaVar("cluster"),
                namespace=GrafanaVar("namespace"),
                container_name=GrafanaVar("container_name"),
            ),
            by="container_name",
        )
        * 100
    )

    label_replaced = LabelReplace(
        kube_limits.labels(
            Label("namespace").matches(GrafanaVar("namespace")),
            Label("container").matches(GrafanaVar("container_name")),
            owner=GrafanaVar("cluster"),
            unit="core",
        ),
        "container",
        "(.+)",
        "container_name",
        "$1",
    )

    max_kube = Max(label_replaced).by("container_name") * 100

    query = max_docker / max_kube

    assert str(query) == compact(
        """
            (
                max(
                    docker_container_cpu_usage_percent{
                        owner="${cluster}",%
                        namespace="${namespace}",%
                        container_name="${container_name}"
                    }
                ) by (container_name) * 100
            )%
            /%
            (
                max(
                    label_replace(
                        kube_pod_container_resource_limits{
                            namespace=~"${namespace}",%
                            container=~"${container_name}",%
                            owner="${cluster}",%
                            unit="core"
                        }
                        , "container_name", "$1"
                        , "container", "(.+)"
                    )
                ) by (container_name) * 100
            )""",
        sub="%: ",
    )


def test_sum_by_multiple_labels_multiply_divide_label_replace() -> None:
    docker_cpu = Metric("docker_container_cpu_usage_percent").labels(
        Label("namespace").matches(GrafanaVar("namespace")),
        Label("container_name").matches(GrafanaVar("container_name")),
        owner=GrafanaVar("cluster"),
    )
    kube_limits = Metric("kube_pod_container_resource_limits").labels(
        Label("namespace").matches(GrafanaVar("namespace")),
        owner=GrafanaVar("cluster"),
        unit="core",
    )

    max_docker = Max(docker_cpu).by("pod_name", "container_name") * 100

    label_replaced = LabelReplace(
        LabelReplace(kube_limits, "container", "container_name"),
        "pod",
        "pod_name",
    )

    max_kube = Max(label_replaced).by("pod_name", "container_name") * 100

    query = max_docker / max_kube

    assert str(query) == compact(
        """
        (
            max(
                docker_container_cpu_usage_percent{
                    namespace=~"${namespace}",%
                    container_name=~"${container_name}",%
                    owner="${cluster}"
                }
            ) by (pod_name, container_name) * 100
        )%
        /%
        (
            max(
                label_replace(
                    label_replace(
                        kube_pod_container_resource_limits{
                            namespace=~"${namespace}",%
                            owner="${cluster}",%
                            unit="core"
                        }
                        , "container_name", "$1"
                        , "container", "(.+)"
                    )
                    , "pod_name", "$1"
                    , "pod", "(.+)"
                )
            ) by (pod_name, container_name) * 100
        )""",
        sub="%: ",
    )


def test_sum_increase_multiply_on_by() -> None:
    kube_resources = Metric("kube_pod_container_status_restarts_total").labels(
        Label("owner").matches(GrafanaVar("cluster")),
        Label("namespace").matches(GrafanaVar("namespace")),
        Label("reason").not_matches("Completed"),
    )

    kube_pod_last_terminated_reason = Metric(
        "kube_pod_container_status_last_terminated_reason"
    ).labels(
        Label("owner").matches(GrafanaVar("cluster")),
        Label("namespace").matches(GrafanaVar("namespace")),
        Label("reason").not_matches("Completed"),
    )

    query = (
        Sum(
            (
                Increase(kube_resources.over(GrafanaVar("__range")))
                * kube_pod_last_terminated_reason
            )
            .on("namespace", "pod", "container")
            .group_left("reason")
        ).by("container", "reason")
        > 0
    )

    assert str(query) == compact(
        """
        sum(
            increase(
                kube_pod_container_status_restarts_total{
                    owner=~"${cluster}",%
                    namespace=~"${namespace}",%
                    reason!~"Completed"
                }
            [${__range}])%
            * on (namespace, pod, container) group_left (reason)%
            kube_pod_container_status_last_terminated_reason{
                owner=~"${cluster}",%
                namespace=~"${namespace}",%
                reason!~"Completed"
            }
        ) by (container, reason) > 0
    """,
        sub="%: ",
    )


def test___():
    """
    deriv(
        (
            sum(
                kafka_consumergroup_lag{
                    owner="prod-kafka-cluster",
                    consumergroup=~"my-consumer-group-.*"
                }
            )
        )[10m:]
    )"""


def test_other():
    sre_discovery = Metric("sre_discovery").labels(
        Label("application").matches(".*my-service.*"),
        Label("application").not_matches(".*excluded-service.*"),
        owner="prod-cluster",
        namespace="my-namespace",
    )

    sre_discovery_shifted = sre_discovery.offset("1h") * 0
    max_sre_discovery = Max(sre_discovery | sre_discovery_shifted).by("version")
    query = Changes(max_sre_discovery["1m":]) > 0

    assert str(query) == compact(
        """
    changes(
        (
            max(
                sre_discovery{
                    application=~\".*my-service.*\",%
                    application!~\".*excluded-service.*\",%
                    owner=\"prod-cluster\",%
                    namespace=\"my-namespace\"
                } or%
                (
                    sre_discovery{
                        application=~\".*my-service.*\",%
                        application!~\".*excluded-service.*\",%
                        owner=\"prod-cluster\",%
                        namespace=\"my-namespace\"
                    } offset 1h * 0
                )
            ) by (version)
        )[1m:]
    ) > 0
    """,
        sub="%: ",
    )
