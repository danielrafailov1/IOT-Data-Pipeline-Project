from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from app.core.database import get_db
from app.models.sensor import SensorReading
from app.services.spc import simple_limits, detect_anomalies_zscore, xbar_r_limits, cusum
from app.services.charts import spc_xbar_chart, spc_cusum_chart, heatmap_chart, pareto_chart
from app.schemas.analytics import ControlLimitsResponse, AnomalyResponse, SPCStatsResponse

router = APIRouter()


def _get_readings(
    db: Session,
    sensor_id: str | None = None,
    sensor_type: str | None = None,
    limit: int = 500,
) -> list[tuple[str, str, float]]:
    """Return list of (sensor_id, sensor_type, value)."""
    q = db.query(SensorReading.sensor_id, SensorReading.sensor_type, SensorReading.value)
    if sensor_id:
        q = q.filter(SensorReading.sensor_id == sensor_id)
    if sensor_type:
        q = q.filter(SensorReading.sensor_type == sensor_type)
    rows = q.order_by(SensorReading.timestamp.desc()).limit(limit).all()
    return [(r[0], r[1], r[2]) for r in rows]


@router.get("/health")
async def analytics_health():
    return {"status": "ok", "service": "analytics"}


@router.get("/spc/stats", response_model=SPCStatsResponse)
async def spc_stats(
    sensor_id: str | None = Query(None, description="Filter by sensor ID"),
    sensor_type: str | None = Query(None, description="Filter by sensor type"),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
):
    """SPC statistics: mean, std, control limits, anomaly indices."""
    rows = _get_readings(db, sensor_id, sensor_type, limit)
    if not rows:
        return SPCStatsResponse(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            mean=0, std=0, min=0, max=0, count=0,
            control_limits=ControlLimitsResponse(center=0, ucl=0, lcl=0, sigma=0),
            anomaly_indices=[],
        )
    values = [r[2] for r in reversed(rows)]
    limits = simple_limits(values)
    anomalies = detect_anomalies_zscore(values)
    return SPCStatsResponse(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        mean=sum(values) / len(values),
        std=(sum((v - sum(values) / len(values)) ** 2 for v in values) / len(values)) ** 0.5 if len(values) > 1 else 0,
        min=min(values),
        max=max(values),
        count=len(values),
        control_limits=ControlLimitsResponse(
            center=limits.center,
            ucl=limits.ucl,
            lcl=limits.lcl,
            sigma=limits.sigma,
        ),
        anomaly_indices=anomalies,
    )


@router.get("/spc/anomalies", response_model=AnomalyResponse)
async def spc_anomalies(
    sensor_id: str | None = Query(None),
    sensor_type: str | None = Query(None),
    limit: int = Query(200, le=1000),
    method: str = Query("zscore", description="zscore or iqr"),
    threshold: float = Query(3.0, description="Z-score threshold"),
    db: Session = Depends(get_db),
):
    """Detect anomalies in sensor readings."""
    from app.services.spc import detect_anomalies_iqr

    rows = _get_readings(db, sensor_id, sensor_type, limit)
    values = [r[2] for r in reversed(rows)]
    if method == "iqr":
        indices = detect_anomalies_iqr(values)
    else:
        indices = detect_anomalies_zscore(values, threshold)
    return AnomalyResponse(indices=indices, method=method, count=len(indices))


@router.get("/charts/spc-xbar")
async def chart_spc_xbar(
    sensor_id: str | None = Query(None),
    sensor_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    subgroup_size: int = Query(5, ge=2, le=10),
    db: Session = Depends(get_db),
):
    """X-bar control chart as Plotly JSON."""
    rows = _get_readings(db, sensor_id, sensor_type, limit)
    values = [r[2] for r in reversed(rows)]
    labels = [r[0] for r in reversed(rows)]
    if not values:
        return Response(content='{"data":[]}', media_type="application/json")
    json_str = spc_xbar_chart(values, labels, subgroup_size)
    return Response(content=json_str, media_type="application/json")


@router.get("/charts/spc-cusum")
async def chart_spc_cusum(
    sensor_id: str | None = Query(None),
    sensor_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """CUSUM chart as Plotly JSON."""
    rows = _get_readings(db, sensor_id, sensor_type, limit)
    values = [r[2] for r in reversed(rows)]
    labels = [r[0] for r in reversed(rows)]
    if not values:
        return Response(content='{"data":[]}', media_type="application/json")
    json_str = spc_cusum_chart(values, labels)
    return Response(content=json_str, media_type="application/json")


@router.get("/charts/heatmap")
async def chart_heatmap(
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    """Heatmap: sensor_type x sensor_id, value = mean reading."""
    rows = db.query(SensorReading.sensor_type, SensorReading.sensor_id, SensorReading.value).order_by(
        SensorReading.timestamp.desc()
    ).limit(limit).all()
    if not rows:
        return Response(content='{"data":[]}', media_type="application/json")
    df = pd.DataFrame(rows, columns=["sensor_type", "sensor_id", "value"])
    pivot = df.pivot_table(index="sensor_type", columns="sensor_id", values="value", aggfunc="mean")
    if pivot.empty or pivot.size < 2:
        return Response(content='{"data":[]}', media_type="application/json")
    json_str = heatmap_chart(df, "sensor_id", "sensor_type", "value")
    return Response(content=json_str, media_type="application/json")


@router.get("/charts/pareto")
async def chart_pareto(
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    """Pareto chart: defect/anomaly count by sensor type."""
    rows = db.query(SensorReading.sensor_type, func.count(SensorReading.id)).group_by(
        SensorReading.sensor_type
    ).limit(20).all()
    if not rows:
        return Response(content='{"data":[]}', media_type="application/json")
    labels = [r[0] for r in rows]
    values = [r[1] for r in rows]
    json_str = pareto_chart(labels, values, title="Readings by Sensor Type (Pareto)")
    return Response(content=json_str, media_type="application/json")


@router.get("/maintenance-summary")
async def maintenance_summary(
    sensor_id: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """AI-generated maintenance summary from recent anomalies and trends."""
    from app.services.maintenance_agent import get_maintenance_summary

    return await get_maintenance_summary(db, sensor_id, limit)
