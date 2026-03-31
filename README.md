# promql-forge

A Python library for programmatically building PromQL queries providing an API to construct metric selectors, label matchers, aggregations, and functions, and renders them as either compact single-line or indented multi-line PromQL strings.

As opposed to [promql-builder](https://pypi.org/project/promql-builder/) from Grafana Labs, this lirary API follows thw SQLAlchemy's fluent style of expression building, leveraging the operators overloading where possible, making the code look more intuitive and closer to the resulting PromQL.

## Features

- Instant vector selectors with label matchers: `=`, `!=`, `=~`, `!~`
- Range vectors and subqueries
- Offset modifier and `@` timestamp modifier
- Binary arithmetic and comparison operators (`+`, `-`, `*`, `/`, `%`, `^`, `>`, `<`, `>=`, `<=`, `==`, `!=`)
- Set operators: `and`, `or`, `unless`
- Vector matching: `.on()`, `.ignoring()`, `.group_left()`, `.group_right()`
- All standard PromQL aggregations: `sum`, `count`, `avg`, `min`, `max`, `topk`, `bottomk`,
  `quantile`, `stddev`, `stdvar`, `group`, `count_values`, `limitk` — with `by`/`without` modifiers
- Full PromQL function library: `rate`, `increase`, `delta`, `histogram_quantile`,
  `label_replace`, `predict_linear`, all `*_over_time` functions, math functions, and more
- Grafana template variable interpolation via `GrafanaVar`
- Compact (single-line) and pretty-printed multi-line output

## Installation

```bash
pip install promql-forge
```

## Usage

All public names are importable directly from `promql_forge`.

### Metric selectors

```python
from promql_forge import Metric, Label, GrafanaVar, to_promql

# Simple selector
str(Metric("http_requests_total"))
# http_requests_total

# Label matchers via keyword arguments or Label objects
m = Metric("http_requests_total")
query = m.labels(
    m.job == "api-server",
    m.env.matches("prod|staging"),    # =~
    m.version.not_matches("v0.*"),    # !~
    status=GrafanaVar("status"),      # Grafana template variable
)
str(query)
# http_requests_total{
#     job="api-server",
#     env=~"prod|staging",
#     version!~"v0.*",
#     status="${status}"
# }

to_promql(query, compact=True)
# http_requests_total{job="api-server",env=~"prod|staging",version!~"v0.*",status="${status}"}
```

### Range vectors, offset, and timestamp

```python
from promql_forge import Metric, Rate, to_promql

# Range vector — compact and pretty-printed
to_promql(Rate(Metric("http_requests_total").labels(job="api").over("5m")), compact=True)
# rate(http_requests_total{job="api"}[5m])

# offset and @ modifiers
str(Metric("foo").labels(env="prod").offset("1h"))
# foo{env="prod"} offset 1h

str(Metric("foo").at("start"))     # foo @ start()
str(Metric("foo") @ 1712000000)    # foo @ 1712000000
```

### Aggregations

```python
from promql_forge import Metric, Sum, Topk, to_promql

# sum by label
str(Sum(Metric("container_cpu_usage"), by="namespace"))
# sum(container_cpu_usage) by (namespace)

# topk with multiple grouping labels; modifier-first rendering
to_promql(Topk(5, Metric("http_requests_total"), by=("job", "status")), modifier_first=True)
# topk by (job, status) (
#     5,
#     http_requests_total
# )
```

### Binary expressions and vector matching

```python
from promql_forge import Metric, Sum, Vector, to_promql

cpu_requests = Sum(Metric("kube_pod_container_resource_requests").labels(resource="cpu"))
cpu_capacity = Sum(Metric("kube_node_status_capacity").labels(resource="cpu"))

to_promql(cpu_requests * 100 / cpu_capacity, compact=True)
# (sum(kube_pod_container_resource_requests{resource="cpu"}) * 100) / sum(kube_node_status_capacity{resource="cpu"})

# Vector matching with many-to-one cardinality
to_promql((Metric("a") * Metric("b")).on("namespace").group_left("pod"), compact=True)
# a * on(namespace) group_left(pod) b

# Set operator fallback
to_promql(Sum(Metric("up")) | Vector(0), compact=True)
# sum(up) or vector(0)
```

### Grafana template variables

`GrafanaVar` renders as `${name}` and can be used anywhere a string value or duration is
accepted, including range selectors.

```python
from promql_forge import Metric, Label, GrafanaVar, Sum, Increase, to_promql

query = Sum(
    Increase(
        Metric("kube_pod_container_status_restarts_total").labels(
            Label("namespace").matches(GrafanaVar("namespace")),
        )[GrafanaVar("__range")]   # variable as range duration
    )
)
to_promql(query, compact=True)
# sum(increase(kube_pod_container_status_restarts_total{namespace=~"${namespace}"}[${__range}]))
```

### Compact vs. pretty-printed output

Every expression implements `to_promql(compact=False)` (default, multi-line) and
`to_promql(compact=True)` (single line). Passing the expression to `str()` is equivalent to
calling `to_promql()` with defaults.

```python
from promql_forge import Metric, Sum, Count, to_promql

query = Count(Sum(Metric("kube_pod_container_status_running").labels(ns="default")).by("pod") >= 1)

to_promql(query, compact=True)
# count(sum(kube_pod_container_status_running{ns="default"}) by(pod) >= 1)

str(query)
# count(
#     sum(
#         kube_pod_container_status_running{ns="default"}
#     ) by (pod) >= 1
# )
```
