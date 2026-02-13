from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TelemetryCreate(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: Optional[str] = None


class TelemetryResponse(BaseModel):
    id: int
    sensor_id: str
    sensor_type: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
