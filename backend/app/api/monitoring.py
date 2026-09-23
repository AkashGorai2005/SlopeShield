from fastapi import APIRouter, HTTPException

from app.services.monitoring_service import monitoring_status, run_monitoring_cycle

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/status")
def status():
    return monitoring_status()


@router.post("/cycle")
def monitoring_cycle():
    try:
        return run_monitoring_cycle()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
