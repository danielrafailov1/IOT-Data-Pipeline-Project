# ZebraStream — IoT Monitoring for Industry 4.0

A full-stack IoT monitoring ecosystem demonstrating real-time data pipelining, Statistical Process Control (SPC), and AI-driven maintenance insights. Built as a portfolio project targeting Industry 4.0 / Smart Manufacturing roles.

---

## Features

- **Real-time telemetry ingestion** — REST API for sensor data with PostgreSQL storage
- **Statistical Process Control (SPC)** — X-bar, R, CUSUM control charts; z-score and IQR anomaly detection
- **Visual analytics** — Plotly dashboards (SPC charts, heatmaps, Pareto)
- **AI maintenance summary** — OpenAI-powered insights and recommendations from anomaly data
- **Orchestration** — Apache Airflow DAGs for scheduled ETL and batch reporting
- **Live dashboard** — Single-page demo with auto-refreshing stats and charts

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI (async, type-hinted) |
| Database | PostgreSQL |
| Orchestration | Apache Airflow |
| Data processing | Pandas, NumPy |
| Visualization | Plotly |
| AI | OpenAI (maintenance agent) |
| DevOps | Docker, Docker Compose |

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- (Optional) OpenAI API key for AI maintenance summaries

### Run

```bash
# 1. Clone and enter project
cd zebra-smart-factory

# 2. Copy env template and set your values
cp .env.example .env
# Edit .env: set POSTGRES_PASSWORD, optionally OPENAI_API_KEY

# 3. Start all services
docker compose up -d

# 4. Load sample data (Airflow)
# Open http://localhost:8080 → login admin/admin → trigger iot_ingestion DAG
```

### URLs

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8000/ |
| **API Docs** | http://localhost:8000/docs |
| **Airflow** | http://localhost:8080 (admin / admin) |

---

## Project Structure

```
zebra-smart-factory/
├── app/                    # FastAPI application
│   ├── api/                # Routes (telemetry, analytics, dashboard)
│   ├── core/               # Config, database
│   ├── models/             # SQLAlchemy ORM
│   ├── schemas/            # Pydantic validation
│   └── services/           # SPC, charts, AI agent
├── dags/                   # Airflow DAGs
├── data_simulator/         # Mock IoT heartbeats
├── tests/                  # Pytest
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/telemetry/` | Ingest sensor reading |
| `GET /api/v1/telemetry/` | List readings |
| `GET /api/v1/analytics/spc/stats` | SPC statistics, control limits |
| `GET /api/v1/analytics/spc/anomalies` | Anomaly detection |
| `GET /api/v1/analytics/charts/*` | Plotly charts (X-bar, CUSUM, heatmap, Pareto) |
| `GET /api/v1/analytics/maintenance-summary` | AI maintenance summary |

---

## Tests

```bash
docker compose exec app pytest tests/ -v
```

---

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — Data flow, Airflow role, simulation vs. production
- [SETUP_INSTRUCTIONS.md](../SETUP_INSTRUCTIONS.md) — Detailed setup and troubleshooting

---

## License

MIT
