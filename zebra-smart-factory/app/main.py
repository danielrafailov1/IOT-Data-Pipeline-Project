from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import telemetry, analytics
from app.api import dashboard
from app.core.database import engine, Base

app = FastAPI(title="ZebraStream IoT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}
