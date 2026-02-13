"""Mock IoT sensor heartbeat generator (JSON)."""
import json
import random
import time
from datetime import datetime
from typing import Generator

SENSOR_TYPES = [
    ("temperature", "celsius", 18, 28),
    ("vibration", "mm/s", 0, 15),
    ("pressure", "psi", 80, 120),
    ("humidity", "%", 30, 70),
]


def generate_heartbeat(sensor_id: str, sensor_type: str, unit: str, low: float, high: float) -> dict:
    return {
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "value": round(random.uniform(low, high), 2),
        "unit": unit,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def stream_heartbeats(interval_sec: float = 2) -> Generator[dict, None, None]:
    """Yield mock sensor heartbeats as JSON-serializable dicts."""
    idx = 0
    while True:
        stype, unit, low, high = SENSOR_TYPES[idx % len(SENSOR_TYPES)]
        sensor_id = f"{stype.upper()[:4]}-{idx % 10:02d}"
        yield generate_heartbeat(sensor_id, stype, unit, low, high)
        idx += 1
        time.sleep(interval_sec)


if __name__ == "__main__":
    for i, hb in enumerate(stream_heartbeats(1)):
        print(json.dumps(hb))
        if i >= 4:
            break
