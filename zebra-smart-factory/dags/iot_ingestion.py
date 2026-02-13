"""ETL DAG: Ingest mock IoT data, transform, load to PostgreSQL."""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import random


def ingest_transform_load():
    """ETL: Generate mock sensor data and load to PostgreSQL."""
    import pandas as pd
    from sqlalchemy import create_engine

    conn_str = (
        f"postgresql://{os.environ.get('POSTGRES_USER', 'zebra_app')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', '')}@"
        f"{os.environ.get('POSTGRES_HOST', 'postgres')}:5432/"
        f"{os.environ.get('POSTGRES_DB', 'zebrastream')}"
    )
    engine = create_engine(conn_str)

    SENSOR_TYPES = [
        ("temperature", "celsius", 18, 28),
        ("vibration", "mm/s", 0, 15),
        ("pressure", "psi", 80, 120),
        ("humidity", "%", 30, 70),
    ]

    rows = []
    for i in range(50):
        stype, unit, low, high = SENSOR_TYPES[i % len(SENSOR_TYPES)]
        sensor_id = f"{stype.upper()[:4]}-{i % 10:02d}"
        value = round(random.uniform(low, high), 2)
        if random.random() < 0.05:
            value = round(random.uniform(low - 5, high + 5), 2)
        rows.append({"sensor_id": sensor_id, "sensor_type": stype, "value": value, "unit": unit})

    df = pd.DataFrame(rows)
    df.to_sql("sensor_readings", engine, if_exists="append", index=False, method="multi")


with DAG(
    dag_id="iot_ingestion",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    tags=["etl", "iot"],
) as dag:
    PythonOperator(
        task_id="ingest_transform_load",
        python_callable=ingest_transform_load,
    )
