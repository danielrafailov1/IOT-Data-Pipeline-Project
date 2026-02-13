from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sensor import SensorReading
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse

router = APIRouter()


@router.post("/", response_model=TelemetryResponse)
async def ingest_telemetry(payload: TelemetryCreate, db: Session = Depends(get_db)):
    reading = SensorReading(
        sensor_id=payload.sensor_id,
        sensor_type=payload.sensor_type,
        value=payload.value,
        unit=payload.unit,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/", response_model=list[TelemetryResponse])
async def list_telemetry(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(limit).all()
