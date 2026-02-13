"""Statistical Process Control (SPC) calculations."""
from typing import NamedTuple
import numpy as np
import pandas as pd


class ControlLimits(NamedTuple):
    """Control chart limits."""
    center: float
    ucl: float  # Upper Control Limit
    lcl: float  # Lower Control Limit
    sigma: float


def xbar_r_limits(values: list[float], subgroup_size: int = 5) -> tuple[ControlLimits, ControlLimits]:
    """
    Calculate X-bar and R chart control limits.
    Uses constants A2, D3, D4 for subgroup sizes 2-10.
    """
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < subgroup_size * 2:
        subgroup_size = max(2, min(n // 2, 10)) if n >= 4 else 2

    # Constants for R chart (D3, D4) and X-bar (A2)
    constants = {
        2: (0, 3.267, 1.880),
        3: (0, 2.574, 1.023),
        4: (0, 2.282, 0.729),
        5: (0, 2.114, 0.577),
        6: (0, 2.004, 0.483),
        7: (0.076, 1.924, 0.419),
        8: (0.136, 1.864, 0.373),
        9: (0.184, 1.816, 0.337),
        10: (0.223, 1.777, 0.308),
    }
    d3, d4, a2 = constants.get(subgroup_size, (0, 2.114, 0.577))

    num_full = (n // subgroup_size) * subgroup_size
    if num_full < subgroup_size:
        return simple_limits(list(arr)), ControlLimits(0, 0, 0, 0)
    subgroups = arr[:num_full].reshape(-1, subgroup_size)
    xbars = np.mean(subgroups, axis=1)
    ranges = np.ptp(subgroups, axis=1)

    xbar_center = np.mean(xbars)
    r_center = np.mean(ranges)

    xbar_ucl = xbar_center + a2 * r_center
    xbar_lcl = xbar_center - a2 * r_center
    r_ucl = d4 * r_center
    r_lcl = d3 * r_center

    return (
        ControlLimits(xbar_center, xbar_ucl, xbar_lcl, np.std(xbars) if len(xbars) > 1 else 0),
        ControlLimits(r_center, r_ucl, r_lcl, np.std(ranges) if len(ranges) > 1 else 0),
    )


def simple_limits(values: list[float], k: float = 3.0) -> ControlLimits:
    """3-sigma limits: center ± k*sigma."""
    arr = np.array(values)
    center = float(np.mean(arr))
    sigma = float(np.std(arr)) if len(arr) > 1 else 0.0
    ucl = center + k * sigma
    lcl = center - k * sigma
    return ControlLimits(center, ucl, lcl, sigma)


def cusum(values: list[float], target: float | None = None, k: float = 0.5) -> list[float]:
    """CUSUM (Cumulative Sum) chart values."""
    arr = np.array(values, dtype=float)
    mu = target if target is not None else float(np.mean(arr))
    sigma = float(np.std(arr)) if len(arr) > 1 and np.std(arr) > 0 else 1.0
    cusum_vals: list[float] = []
    c = 0.0
    for v in arr:
        c = max(0.0, c + (v - mu) - k * sigma)
        cusum_vals.append(float(c))
    return cusum_vals


def detect_anomalies_zscore(values: list[float], threshold: float = 3.0) -> list[int]:
    """Return indices of values that exceed z-score threshold."""
    arr = np.array(values)
    if len(arr) < 2:
        return []
    mean = np.mean(arr)
    std = np.std(arr)
    if std == 0:
        return []
    z = np.abs((arr - mean) / std)
    return [int(i) for i in np.where(z > threshold)[0]]


def detect_anomalies_iqr(values: list[float], k: float = 1.5) -> list[int]:
    """Return indices of values outside IQR-based bounds."""
    arr = np.array(values)
    if len(arr) < 4:
        return []
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return [int(i) for i in np.where((arr < lower) | (arr > upper))[0]]
