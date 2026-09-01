"""
SLARAP Lightweight Predictive Analytics.

Implements:
- Moving average
- Exponential smoothing (EWMA)
- Linear regression forecast
- Trend classification
"""

from typing import Any

from backend import config
from backend.storage import db


def moving_average(series: list[float], window: int = 5) -> float:
    """Calculate the moving average of the last `window` points."""

    if not series:
        return 0.0
    window = min(window, len(series))
    return sum(series[-window:]) / window


def exponential_smoothing(series: list[float], alpha: float = 0.3) -> float:
    """Exponentially weighted moving average (EWMA)."""

    if not series:
        return 0.0
    smoothed = series[0]
    for value in series[1:]:
        smoothed = alpha * value + (1 - alpha) * smoothed
    return smoothed


def linear_regression(series: list[float]) -> tuple[float, float]:
    """
    Compute (slope, intercept) for y = slope * x + intercept.
    x = 0, 1, 2, ..., n-1.
    """

    n = len(series)
    if n < 2:
        return 0.0, (series[0] if series else 0.0)

    sum_x = sum(range(n))
    sum_y = sum(series)
    sum_xx = sum(i * i for i in range(n))
    sum_xy = sum(i * v for i, v in enumerate(series))

    denominator = n * sum_xx - sum_x * sum_x
    if denominator == 0:
        return 0.0, sum_y / n

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def forecast(
    series: list[float],
    steps: int | None = None,
    window: int | None = None,
    clamp: tuple[float, float] | None = (0, 100),
) -> tuple[list[float], float]:
    """
    Return (list of future predictions, slope).
    Uses linear regression on a window + blending with moving average.
    """

    steps = steps or config.PREDICTION_STEPS
    window = window or config.PREDICTION_WINDOW

    data = series[-window:]
    if not data:
        return [0.0] * steps, 0.0

    slope, intercept = linear_regression(data)
    n = len(data)
    predictions = []

    for i in range(1, steps + 1):
        future_x = n - 1 + i
        predicted = slope * future_x + intercept
        # Blend with moving average to damp noise
        blended = 0.6 * predicted + 0.4 * moving_average(data, 5)
        if clamp:
            blended = max(clamp[0], min(clamp[1], blended))
        predictions.append(round(blended, 2))

    return predictions, slope


def trend_label(slope: float, eps: float = 0.05) -> str:
    """Return a label indicating if the slope is rising, falling, or stable."""

    if slope > eps:
        return "RISING"
    if slope < -eps:
        return "FALLING"
    return "STABLE"


def predict_all(monitor=None, hours: int = 24) -> dict[str, Any]:
    """
    Predict CPU, memory, and disk usage.
    Uses in-memory monitor history if available, otherwise database.
    """

    if monitor and len(monitor.get_series("cpu")) >= 10:
        cpu = monitor.get_series("cpu")
        memory = monitor.get_series("memory")
        disk = monitor.get_series("disk")
    else:
        rows = db.metrics_since(hours * 3600)
        cpu = [row["cpu"] for row in rows]
        memory = [row["memory"] for row in rows]
        disk = [row["disk"] for row in rows]

    result = {}

    for name, series in (("cpu", cpu), ("memory", memory), ("disk", disk)):
        predictions, slope = forecast(series)
        result[name] = {
            "current": round(series[-1], 2) if series else 0.0,
            "moving_avg": round(moving_average(series, 10), 2),
            "ewma": round(exponential_smoothing(series), 2),
            "forecast": predictions,
            "next": predictions[0] if predictions else 0.0,
            "horizon": predictions[-1] if predictions else 0.0,
            "slope": round(slope, 4),
            "trend": trend_label(slope),
            "samples": len(series),
        }

    # Disk growth estimate (pct/day)
    rows = db.metrics_since(24 * 3600)
    if len(rows) >= 20:
        first_ts = rows[0]["timestamp"]
        last_ts = rows[-1]["timestamp"]
        span_hours = (last_ts - first_ts) / 3600.0
        if span_hours > 0.1:
            disk_change = rows[-1]["disk"] - rows[0]["disk"]
            daily_growth = disk_change / span_hours * 24
            result["disk"]["growth_per_day"] = round(daily_growth, 3)

            free_pct = 100 - rows[-1]["disk"]
            if daily_growth > 0.01:
                result["disk"]["days_until_full"] = round(free_pct / daily_growth, 1)
            else:
                result["disk"]["days_until_full"] = None

    return result


def format_predictions(predictions: dict[str, Any]) -> str:
    """Return a human-readable string of the prediction report."""

    lines = ["=" * 70, "PREDICTIVE ANALYTICS", "=" * 70]

    for resource, data in predictions.items():
        lines.append(f"\n[{resource.upper()}]")
        lines.append(f"  Samples   : {data['samples']}")
        lines.append(f"  Current   : {data['current']}%")
        lines.append(f"  MA(10)    : {data['moving_avg']}%")
        lines.append(f"  EWMA      : {data['ewma']}%")
        lines.append(f"  Trend     : {data['trend']}  (slope {data['slope']}/sample)")
        lines.append(f"  Next      : {data['next']}%")
        lines.append(f"  Horizon   : {data['horizon']}%  (+{len(data['forecast'])} steps)")
        lines.append("  Curve     : " + " ".join(f"{x:.0f}" for x in data["forecast"]))

        if resource == "disk" and data.get("growth_per_day") is not None:
            lines.append(f"  Growth    : {data['growth_per_day']}%/day")
            if data.get("days_until_full"):
                lines.append(f"  FULL IN   : ~{data['days_until_full']} days")

    lines.append("=" * 70)
    return "\n".join(lines)
