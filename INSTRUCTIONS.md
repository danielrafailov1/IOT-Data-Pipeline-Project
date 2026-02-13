# Project Blueprint: ZebraStream Industry 4.0
**Target Role:** Software Engineer Intern (Industry 4.0 / Smart Manufacturing)
**Company:** Zebra Technologies
**Objective:** A high-fidelity IoT monitoring ecosystem demonstrating real-time data pipelining, Statistical Process Control (SPC), and AI-driven maintenance insights.

---

## 🛠 Tech Stack Requirements
* **Language:** Python 3.10+ (Type-hinted & OOP)
* **Orchestration:** Apache Airflow (Docker-based)
* **API Framework:** FastAPI (Async)
* **Data Processing:** Pandas & NumPy (ETL & Statistics)
* **Visualization:** Plotly (SPC, Heatmaps, Pareto Charts)
* **Database:** PostgreSQL (Relational Sensor History)
* **DevOps:** Docker & Docker Compose
* **AI Layer:** LangChain / OpenAI (Maintenance Summary Agent)

---

## 📂 Architecture & Folder Structure

[Image of a software architecture diagram showing IoT data ingestion to Airflow, storage in PostgreSQL, and visualization via a FastAPI dashboard]

```text
zebra-smart-factory/
├── app/                    # FastAPI Application Layer
│   ├── main.py             # Entry point
│   ├── api/                # Route Handlers
│   │   └── v1/             # Versioned Endpoints
│   │       ├── telemetry.py
│   │       └── analytics.py
│   ├── core/               # Config & Database Session
│   ├── models/             # SQLAlchemy ORM Models
│   ├── schemas/            # Pydantic Validation Schemas
│   └── services/           # Business Logic (SPC & Anomaly Detection)
├── dags/                   # Airflow Orchestration
│   ├── iot_ingestion.py    # ETL: Ingest -> Transform -> Load
│   └── daily_summary.py    # Batch Report Generation
├── data_simulator/         # Mock IoT Sensor Heartbeats (JSON)
├── tests/                  # Pytest Unit & Integration Tests
├── docker-compose.yml      # Multi-container Setup (App, DB, Airflow)
├── Dockerfile              # App Containerization
└── requirements.txt        # Dependency Manifest