import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth, predictions, locations, sensors, alerts, reports, data, monitoring
from app.database.database import init_db
from app.services.monitoring_service import run_monitoring_cycle

settings = get_settings()

init_db()


async def monitoring_loop():
    while True:
        try:
            await asyncio.to_thread(run_monitoring_cycle)
        except Exception as exc:
            print(f"Automatic monitoring cycle failed: {exc}")
        await asyncio.sleep(max(1, settings.monitoring_interval_minutes * 60))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = None
    if settings.monitoring_enabled:
        task = asyncio.create_task(monitoring_loop())
    try:
        yield
    finally:
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "SLOPESHIELD NER",
        "environment": settings.environment,
        "docs": "/docs"
    }


@app.get("/")
def root():
    return {
        "project": "SLOPESHIELD NER API",
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
        "frontend": "http://127.0.0.1:5173/",
    }


@app.get("/api/status")
def status():
    from app.services.ml_service import ml_service
    from app.services.data_service import data_status

    return {
        "project": "SLOPESHIELD NER",
        "modelTrained": ml_service.trained,
        "modelSource": ml_service.model_source,
        "data": data_status(),
        "iot": False
    }


app.include_router(auth.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
