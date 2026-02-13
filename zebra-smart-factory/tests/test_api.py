"""API tests."""
import pytest
from app.models.sensor import SensorReading


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_telemetry_post(client):
    r = client.post(
        "/api/v1/telemetry/",
        json={"sensor_id": "TEMP-01", "sensor_type": "temperature", "value": 23.5, "unit": "celsius"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["sensor_id"] == "TEMP-01"
    assert data["value"] == 23.5
    assert "id" in data


def test_telemetry_list(client):
    client.post("/api/v1/telemetry/", json={"sensor_id": "T-1", "sensor_type": "temp", "value": 22.0})
    r = client.get("/api/v1/telemetry/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_analytics_health(client):
    r = client.get("/api/v1/analytics/health")
    assert r.status_code == 200
    assert r.json()["service"] == "analytics"


def test_spc_stats_empty(client):
    r = client.get("/api/v1/analytics/spc/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 0
    assert "control_limits" in data


def test_spc_stats_with_data(client):
    for i in range(10):
        client.post(
            "/api/v1/telemetry/",
            json={"sensor_id": "T-1", "sensor_type": "temp", "value": 22.0 + i * 0.1},
        )
    r = client.get("/api/v1/analytics/spc/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 10
    assert data["mean"] > 0
    assert "control_limits" in data
