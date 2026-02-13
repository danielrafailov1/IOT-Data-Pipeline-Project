"""SPC service tests."""
import pytest
from app.services.spc import (
    simple_limits,
    xbar_r_limits,
    cusum,
    detect_anomalies_zscore,
    detect_anomalies_iqr,
)


def test_simple_limits():
    values = [10.0, 11.0, 12.0, 13.0, 14.0]
    limits = simple_limits(values)
    assert limits.center == 12.0
    assert limits.ucl > limits.center
    assert limits.lcl < limits.center


def test_cusum():
    values = [10.0, 11.0, 12.0, 13.0, 14.0]
    c = cusum(values)
    assert len(c) == len(values)
    assert all(v >= 0 for v in c)


def test_detect_anomalies_zscore():
    values = [10.0, 10.1, 10.2, 10.1, 10.0, 100.0]
    indices = detect_anomalies_zscore(values, threshold=3.0)
    assert 5 in indices


def test_detect_anomalies_zscore_no_anomaly():
    values = [10.0, 10.1, 10.2, 10.1, 10.0]
    indices = detect_anomalies_zscore(values)
    assert len(indices) == 0


def test_detect_anomalies_iqr():
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]
    indices = detect_anomalies_iqr(values)
    assert 5 in indices


def test_xbar_r_limits():
    values = list(range(20))
    xbar_lim, r_lim = xbar_r_limits(values, subgroup_size=5)
    assert xbar_lim.center > 0
    assert xbar_lim.ucl > xbar_lim.lcl
