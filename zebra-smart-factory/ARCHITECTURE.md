# ZebraStream Architecture: How Data Flows (and How We Simulate It)

## The Big Picture

In a **real smart factory**, IoT machines (sensors on conveyor belts, motors, temperature probes, etc.) continuously emit telemetry. That data flows through message queues or APIs into a database, where analytics and AI process it.

We don't have real machines. So we **simulate** the entire flow. Here's how.

---

## Real Factory vs. Our Demo

| Real Factory | Our Demo |
|--------------|----------|
| Machines emit MQTT/HTTP | We generate fake data in code |
| Kafka/RabbitMQ buffers messages | No queue — we write directly to DB or POST to API |
| Airflow pulls from queue, transforms, loads | Airflow runs Python that generates + loads in one step |
| Data arrives 24/7 | Data arrives when DAGs run (hourly/daily) or when we run the simulator |

---

## How Apache Airflow Works in This Project

### What Airflow Does

Airflow is an **orchestrator**. It:

1. **Schedules** when tasks run (e.g., every hour, every day)
2. **Runs** Python code (or other tasks) at those times
3. **Tracks** success/failure and retries

It does **not** connect to real machines. It runs **our code**, which either:

- Generates fake data and writes to the database, or
- Fetches from an API (in our case, we could have the simulator POST to the API, and a DAG could trigger the simulator — but we kept it simpler)

### Our Two Simulation Paths

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PATH A: Airflow DAG (iot_ingestion)                                     │
│  ───────────────────────────────────                                    │
│  Runs hourly → Python generates 50 fake readings → Writes to PostgreSQL  │
│  (No real machines. The DAG IS the data source.)                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  PATH B: Data Simulator (optional)                                       │
│  ────────────────────────────────                                       │
│  python -m data_simulator.run → Generates heartbeats → POSTs to FastAPI │
│  FastAPI → Writes to PostgreSQL                                          │
│  (Simulates machines sending HTTP to our API.)                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### What Would Change With Real Machines

| Component | Today (Simulated) | With Real Machines |
|-----------|-------------------|--------------------|
| **Data source** | Python `random.uniform()` in DAG | MQTT broker, Kafka, or machine HTTP API |
| **Airflow DAG** | Generates + loads in one task | Task 1: Pull from Kafka. Task 2: Transform. Task 3: Load to DB |
| **Ingestion** | Direct `to_sql()` or FastAPI POST | Message consumer → batch insert |

---

## End-to-End Flow (Current Demo)

```
                    ┌──────────────────┐
                    │  Airflow         │
                    │  (scheduler)     │
                    └────────┬─────────┘
                             │ every hour
                             ▼
                    ┌──────────────────┐
                    │  iot_ingestion   │
                    │  DAG             │
                    │  (generates 50   │
                    │   fake readings) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  PostgreSQL      │
                    │  sensor_readings │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
  │  FastAPI    │   │  SPC /      │   │  Maintenance     │
  │  /telemetry │   │  Analytics  │   │  Summary (AI)    │
  │  /docs      │   │  Charts     │   │                  │
  └─────────────┘   └─────────────┘   └─────────────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Dashboard       │
                    │  / or /dashboard │
                    └──────────────────┘
```

---

## Summary

- **Airflow** = Scheduler that runs our Python code on a schedule.
- **Data source** = Simulated. The `iot_ingestion` DAG generates fake sensor data and loads it into PostgreSQL.
- **Real machines** would replace the "generate fake data" step with "pull from MQTT/Kafka/API."
- The rest (PostgreSQL, FastAPI, SPC, AI, dashboard) would work the same with real data.
