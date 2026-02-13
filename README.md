<img width="855" height="242" alt="Screenshot 2026-02-13 at 12 28 06 AM" src="https://github.com/user-attachments/assets/8d1448fb-eca7-4fa9-92c8-d57f04e2a2e7" /><img width="1703" height="982" alt="Screenshot 2026-02-13 at 12 26 52 AM" src="https://github.com/user-attachments/assets/9c2905db-1ed2-4b43-947d-078168b0247b" /><img width="1701" height="983" alt="Screenshot 2026-02-13 at 12 26 12 AM" src="https://github.com/user-attachments/assets/d0a7a040-0421-4b30-a0f9-93ddca01b44d" /># ZebraStream — IoT Monitoring for Industry 4.0

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

# 4. Load sample data
# Option A (local): Open http://localhost:8080 → login admin/admin → trigger iot_ingestion DAG
# Option B (deployed): API_URL=https://zebrastream.onrender.com python -m data_simulator.run
```

### URLs

**Live demo (deployed on Render):**

| Service | URL |
|---------|-----|
| **Dashboard** | https://zebrastream.onrender.com/ |
| **API Docs** | https://zebrastream.onrender.com/docs |

**Local development:**

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:8000/ |
| **API Docs** | http://localhost:8000/docs |
| **Airflow** | http://localhost:8080 (admin / admin) |

---

## Screenshots

| Dashboard | Analytics |
|-----------|-----------|
| ![Uploading Screenshot 2026-02-13 at 12.26.52 AM.png…] |![Uploading Screenshot 2026-02-13 at 12.28.06 AM.png…]|

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

## Data Generation

Mock data does **not** auto-generate. To add data:

- **Local:** Trigger the `iot_ingestion` DAG in Airflow (runs once per trigger).
- **Deployed:** Run `API_URL=https://zebrastream.onrender.com python -m data_simulator.run` from `zebra-smart-factory` (posts 50 readings once).

---

## License

MIT
