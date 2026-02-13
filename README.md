# IoT Data Pipeline Project

Portfolio project: **ZebraStream** — an IoT monitoring ecosystem for Industry 4.0 / Smart Manufacturing.

## Quick Links

- **[zebra-smart-factory/](zebra-smart-factory/)** — Main application (FastAPI, Airflow, PostgreSQL)
- **[zebra-smart-factory/README.md](zebra-smart-factory/README.md)** — Setup, features, tech stack
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** — Detailed setup and troubleshooting

## Run

```bash
cd zebra-smart-factory
cp .env.example .env   # Edit with your POSTGRES_PASSWORD
docker compose up -d
```

Dashboard: http://localhost:8000/ · Airflow: http://localhost:8080 (admin/admin)
