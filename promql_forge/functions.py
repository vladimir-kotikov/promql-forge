from typing import overload

from promql_forge.expressions import Function
from promql_forge.models import GrafanaVar
from promql_forge.util import quote
from promql_forge.vectors import InstantVector, RangeVector

type NumericParam = int | float | GrafanaVar


def Abs(vector: InstantVector) -> Function:
    return Function("abs", vector)


def Absent(vector: InstantVector) -> Function:
    return Function("absent", vector)


def AbsentOverTime(range_vector: RangeVector) -> Function:
    return Function("absent_over_time", range_vector)


def Ceil(vector: InstantVector) -> Function:
    return Function("ceil", vector)


def Changes(range_vector: RangeVector) -> Function:
    return Function("changes", range_vector)


def Clamp(vector: InstantVector, min: NumericParam, max: NumericParam) -> Function:
    return Function("clamp", vector, min, max)


def ClampMax(vector: InstantVector, max: NumericParam) -> Function:
    return Function("clamp_max", vector, max)


def ClampMin(vector: InstantVector, min: NumericParam) -> Function:
    return Function("clamp_min", vector, min)


def DayOfMonth(vector: InstantVector) -> Function:
    return Function("day_of_month", vector)


def DayOfWeek(vector: InstantVector) -> Function:
    return Function("day_of_week", vector)


def DayOfYear(vector: InstantVector) -> Function:
    return Function("day_of_year", vector)


def DaysInMonth(vector: InstantVector) -> Function:
    return Function("days_in_month", vector)


def Delta(range_vector: RangeVector) -> Function:
    return Function("delta", range_vector)


def Deriv(range_vector: RangeVector) -> Function:
    return Function("deriv", range_vector)


def Exp(vector: InstantVector) -> Function:
    return Function("exp", vector)


def Floor(vector: InstantVector) -> Function:
    return Function("floor", vector)


def HistogramAvg(vector: InstantVector) -> Function:
    return Function("histogram_avg", vector)


def HistogramCount(vector: InstantVector) -> Function:
    return Function("histogram_count", vector)


def HistogramFraction(lower: NumericParam, upper: NumericParam, vector: InstantVector):
    return Function("histogram_fraction", lower, upper, vector)


def HistogramQuantile(phi: NumericParam, vector: InstantVector):
    if isinstance(phi, (int, float)) and not (0 <= phi <= 1):
        raise ValueError("Quantile must be between 0 and 1")

    return Function("histogram_quantile", phi, vector)


def HistogramStddev(vector: InstantVector) -> Function:
    return Function("histogram_stddev", vector)


def HistogramStdvar(vector: InstantVector) -> Function:
    return Function("histogram_stdvar", vector)


def Hour(vector: InstantVector) -> Function:
    return Function("hour", vector)


def Idelta(range_vector: RangeVector) -> Function:
    return Function("idelta", range_vector)


def Increase(range_vector: RangeVector) -> Function:
    return Function("increase", range_vector)


def Irate(range_vector: RangeVector) -> Function:
    return Function("irate", range_vector)


def LabelJoin(
    vector: InstantVector,
    dest_label: str,
    separator: str,
    *source_labels: str,
) -> Function:
    return Function(
        "label_join",
        vector,
        *(quote(arg) for arg in (dest_label, separator, *source_labels)),
    )


@overload
def LabelReplace(vector: InstantVector, from_: str, to: str): ...
@overload
def LabelReplace(
    vector: InstantVector, from_: str, regex: str, to: str, replacement: str
): ...
def LabelReplace(vector: InstantVector, *args: str) -> Function:
    if len(args) == 2:
        from_, to = args
        _args = [to, "$1", from_, "(.+)"]
    elif len(args) == 4:
        from_, regex, to, replacement = args
        _args = [to, replacement, from_, regex]
    else:
        raise ValueError("Invalid number of arguments for LabelReplace")

    return Function("label_replace", vector, *(quote(arg) for arg in _args))


def Ln(vector: InstantVector) -> Function:
    return Function("ln", vector)


def Log2(vector: InstantVector) -> Function:
    return Function("log2", vector)


def Log10(vector: InstantVector) -> Function:
    return Function("log10", vector)


def Minute(vector: InstantVector) -> Function:
    return Function("minute", vector)


def Month(vector: InstantVector) -> Function:
    return Function("month", vector)


def PredictLinear(range_vector: RangeVector, t: float) -> Function:
    return Function("predict_linear", range_vector, t)


def Rate(range_vector: RangeVector) -> Function:
    return Function("rate", range_vector)


def Resets(range_vector: RangeVector) -> Function:
    return Function("resets", range_vector)


def Round(vector: InstantVector) -> Function:
    return Function("round", vector)


def Scalar(vector: InstantVector) -> Function:
    return Function("scalar", vector)


def Sgn(vector: InstantVector) -> Function:
    return Function("sgn", vector)


def Sort(vector: InstantVector) -> Function:
    return Function("sort", vector)


def SortDesc(vector: InstantVector) -> Function:
    return Function("sort_desc", vector)


def Sqrt(vector: InstantVector):
    return Function("sqrt", vector)


def Time() -> Function:
    return Function("time")


def Timestamp(vector: InstantVector) -> Function:
    return Function("timestamp", vector)


def Vector(scalar: NumericParam) -> Function:
    return Function("vector", scalar)


def Year(vector: InstantVector) -> Function:
    return Function("year", vector)


def AvgOverTime(range_vector: RangeVector) -> Function:
    return Function("avg_over_time", range_vector)


def MinOverTime(range_vector: RangeVector) -> Function:
    return Function("min_over_time", range_vector)


def MaxOverTime(range_vector: RangeVector) -> Function:
    return Function("max_over_time", range_vector)


def SumOverTime(range_vector: RangeVector) -> Function:
    return Function("sum_over_time", range_vector)


def CountOverTime(range_vector: RangeVector) -> Function:
    return Function("count_over_time", range_vector)


def QuantileOverTime(quantile: float, range_vector: RangeVector) -> Function:
    return Function("quantile_over_time", quantile, range_vector)


def StddevOverTime(range_vector: RangeVector) -> Function:
    return Function("stddev_over_time", range_vector)


def StdvarOverTime(range_vector: RangeVector) -> Function:
    return Function("stdvar_over_time", range_vector)


def LastOverTime(range_vector: RangeVector) -> Function:
    return Function("last_over_time", range_vector)


def Acos(vector: InstantVector) -> Function:
    return Function("acos", vector)


def Acosh(vector: InstantVector) -> Function:
    return Function("acosh", vector)


def Asin(vector: InstantVector) -> Function:
    return Function("asin", vector)


def Asinh(vector: InstantVector) -> Function:
    return Function("asinh", vector)


def Atan(vector: InstantVector) -> Function:
    return Function("atan", vector)


def Atanh(vector: InstantVector) -> Function:
    return Function("atanh", vector)


def Cos(vector: InstantVector) -> Function:
    return Function("cos", vector)


def Cosh(vector: InstantVector) -> Function:
    return Function("cosh", vector)


def Sin(vector: InstantVector) -> Function:
    return Function("sin", vector)


def Sinh(vector: InstantVector) -> Function:
    return Function("sinh", vector)


def Tan(vector: InstantVector) -> Function:
    return Function("tan", vector)


def Tanh(vector: InstantVector) -> Function:
    return Function("tanh", vector)


def Deg(vector: InstantVector) -> Function:
    return Function("deg", vector)


def Rad(vector: InstantVector) -> Function:
    return Function("rad", vector)


def Pi() -> Function:
    return Function("pi")
