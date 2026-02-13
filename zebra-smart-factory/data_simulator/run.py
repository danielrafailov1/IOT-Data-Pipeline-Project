"""Run the data simulator: generate heartbeats and POST to the API."""
import os
import sys
import time
import random
import httpx
from data_simulator.simulator import SENSOR_TYPES, generate_heartbeat

API_URL = os.environ.get("API_URL", "http://app:8000")


def run(count: int = 50, interval_sec: float = 0.5) -> None:
    """Generate and POST sensor readings to the API."""
    url = f"{API_URL}/api/v1/telemetry/"
    posted = 0
    errors = 0
    for i in range(count):
        stype, unit, low, high = SENSOR_TYPES[i % len(SENSOR_TYPES)]
        sensor_id = f"{stype.upper()[:4]}-{i % 10:02d}"
        # Occasionally inject an anomaly (out of range)
        if random.random() < 0.05:
            high, low = high + 5, low - 5
        payload = generate_heartbeat(sensor_id, stype, unit, low, high)
        payload.pop("timestamp", None)
        try:
            r = httpx.post(url, json=payload, timeout=5)
            if r.is_success:
                posted += 1
            else:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"Error: {e}", file=sys.stderr)
        time.sleep(interval_sec)
    print(f"Posted {posted} readings, {errors} errors")


if __name__ == "__main__":
    n = int(os.environ.get("SIMULATOR_COUNT", "50"))
    run(count=n)
