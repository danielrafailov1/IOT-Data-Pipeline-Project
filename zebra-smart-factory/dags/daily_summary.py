"""Batch DAG: Daily report generation and maintenance summary."""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import os


def generate_daily_report():
    """Generate daily summary statistics from sensor readings."""
    import pandas as pd
    from sqlalchemy import create_engine

    conn_str = (
        f"postgresql://{os.environ.get('POSTGRES_USER', 'zebra_app')}:"
        f"{os.environ.get('POSTGRES_PASSWORD', '')}@"
        f"{os.environ.get('POSTGRES_HOST', 'postgres')}:5432/"
        f"{os.environ.get('POSTGRES_DB', 'zebrastream')}"
    )
    engine = create_engine(conn_str)
    df = pd.read_sql(
        "SELECT sensor_type, sensor_id, value, timestamp FROM sensor_readings ORDER BY timestamp DESC LIMIT 1000",
        engine,
    )
    summary = df.groupby("sensor_type").agg({"value": ["mean", "std", "min", "max"], "sensor_id": "count"})
    print(summary)
    print(f"\nTotal readings: {len(df)}")


with DAG(
    dag_id="daily_summary",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["report", "batch"],
) as dag:
    PythonOperator(
        task_id="generate_daily_report",
        python_callable=generate_daily_report,
    )
