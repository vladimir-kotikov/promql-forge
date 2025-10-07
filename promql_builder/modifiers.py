from promql_builder.models import LabelModifier

type AggregationModifier = By | Without
type ExpressionLabelsModifier = On | Ignoring
type ExpressionGroupModifier = GroupLeft | GroupRight


class By(LabelModifier, name="by"): ...


class Without(LabelModifier, name="without"): ...


class On(LabelModifier, name="on"): ...


class Ignoring(LabelModifier, name="ignoring"): ...


class GroupLeft(LabelModifier, name="group_left"): ...


class GroupRight(LabelModifier, name="group_right"): ...
