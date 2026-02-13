"""LangChain/OpenAI maintenance summary agent."""
from typing import Any
from sqlalchemy.orm import Session
from app.models.sensor import SensorReading
from app.services.spc import simple_limits, detect_anomalies_zscore
from app.core.config import get_settings


async def get_maintenance_summary(
    db: Session,
    sensor_id: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Generate AI maintenance summary from recent sensor data and anomalies.
    Falls back to a structured summary if OpenAI key is missing.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return _fallback_summary(db, sensor_id, limit)

    q = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.filter(SensorReading.sensor_id == sensor_id)
    readings = q.all()

    if not readings:
        return {"summary": "No sensor data available.", "anomalies": [], "recommendations": []}

    # Build context for LLM
    by_type: dict[str, list[float]] = {}
    for r in readings:
        key = f"{r.sensor_id} ({r.sensor_type})"
        if key not in by_type:
            by_type[key] = []
        by_type[key].append(r.value)

    anomalies_found: list[dict[str, Any]] = []
    for key, values in by_type.items():
        if len(values) < 3:
            continue
        limits = simple_limits(values)
        indices = detect_anomalies_zscore(values)
        for i in indices:
            anomalies_found.append({
                "sensor": key,
                "value": values[i],
                "ucl": limits.ucl,
                "lcl": limits.lcl,
            })

    context = (
        f"Sensor readings summary: {len(readings)} total. "
        f"By sensor: " + ", ".join(f"{k}: n={len(v)}, mean={sum(v)/len(v):.2f}" for k, v in by_type.items()) + ". "
    )
    if anomalies_found:
        context += f" Anomalies detected: {len(anomalies_found)}. Details: " + str(anomalies_found[:5])

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a maintenance engineer for a smart factory. Be concise and actionable."},
                {"role": "user", "content": f"Based on this IoT sensor data:\n\n{context}\n\nProvide a brief maintenance summary (2-4 sentences) and 1-3 specific recommendations."},
            ],
            temperature=0.3,
        )
        summary_text = response.choices[0].message.content or "No summary generated."
    except Exception as e:
        summary_text = _fallback_summary(db, sensor_id, limit)["summary"]
        summary_text += f" (AI unavailable: {e})"

    return {
        "summary": summary_text,
        "anomalies": anomalies_found[:10],
        "recommendations": _default_recommendations(anomalies_found),
    }


def _fallback_summary(db: Session, sensor_id: str | None, limit: int) -> dict[str, Any]:
    """Non-AI fallback when OpenAI is unavailable."""
    q = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.filter(SensorReading.sensor_id == sensor_id)
    readings = q.all()
    if not readings:
        return {"summary": "No data.", "anomalies": [], "recommendations": []}

    by_type: dict[str, list[float]] = {}
    for r in readings:
        key = r.sensor_type
        if key not in by_type:
            by_type[key] = []
        by_type[key].append(r.value)

    anomalies = []
    for key, values in by_type.items():
        if len(values) >= 3:
            indices = detect_anomalies_zscore(values)
            for i in indices:
                anomalies.append({"sensor": key, "value": values[i]})

    summary = (
        f"Total readings: {len(readings)}. "
        f"Sensor types: {', '.join(by_type.keys())}. "
        f"Anomalies detected: {len(anomalies)}."
    )
    return {
        "summary": summary,
        "anomalies": anomalies[:10],
        "recommendations": _default_recommendations(anomalies),
    }


def _default_recommendations(anomalies: list[dict]) -> list[str]:
    """Default recommendations based on anomaly count."""
    recs = []
    if len(anomalies) > 5:
        recs.append("Schedule preventive maintenance - multiple anomalies detected.")
    if len(anomalies) > 0:
        recs.append("Review sensor calibration for flagged sensors.")
    if not recs:
        recs.append("No immediate action required. Continue routine monitoring.")
    return recs
