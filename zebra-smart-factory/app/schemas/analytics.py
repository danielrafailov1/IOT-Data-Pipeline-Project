from pydantic import BaseModel
from typing import Optional


class ControlLimitsResponse(BaseModel):
    center: float
    ucl: float
    lcl: float
    sigma: float


class AnomalyResponse(BaseModel):
    indices: list[int]
    method: str
    count: int


class SPCStatsResponse(BaseModel):
    sensor_id: Optional[str] = None
    sensor_type: Optional[str] = None
    mean: float
    std: float
    min: float
    max: float
    count: int
    control_limits: ControlLimitsResponse
    anomaly_indices: list[int]
