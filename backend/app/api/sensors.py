from fastapi import APIRouter
router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.get("/status")
def sensor_status():
    return {"enabled": False, "message": "IoT, ESP32, physical sensors and sensor simulation are intentionally disabled for SLOPESHIELD NER."}
