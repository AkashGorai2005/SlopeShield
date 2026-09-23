from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.database.schemas import PredictionOut, SimulationIn
from app.services.data_service import get_location
from app.services.ml_service import ml_service


router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],
)


def _features(item, rainfall=None):
    rain = float(
        item.get("rainfall", 0)
        if rainfall is None
        else rainfall
    )

    rainfall_7d = float(
        item.get("rainfall7d", 0) or 0
    )

    return {
        "rainfall_24h": rain,
        "rainfall_7d": rainfall_7d,
        "elevation": float(
            item.get("elevation", 0) or 0
        ),
        "slope": float(
            item.get("slope", 0) or 0
        ),
        "historical_landslides": float(
            item.get("historicalLandslides", 0) or 0
        ),
    }


def _save_prediction(
    location_id: str,
    probability: float,
    risk_level: str,
    model_name: str,
    features: dict,
):
    query = text(
        """
        INSERT INTO risk_predictions (
            location_id,
            probability,
            risk_level,
            model_name,
            rainfall_24h,
            rainfall_7d,
            elevation,
            slope,
            historical_landslides,
            created_at
        )
        VALUES (
            :location_id,
            :probability,
            :risk_level,
            :model_name,
            :rainfall_24h,
            :rainfall_7d,
            :elevation,
            :slope,
            :historical_landslides,
            CURRENT_TIMESTAMP
        )
        """
    )

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "location_id": location_id,
                "probability": probability,
                "risk_level": risk_level,
                "model_name": model_name,
                **features,
            },
        )


@router.post(
    "/simulate",
    response_model=PredictionOut,
)
def simulate(payload: SimulationIn):
    item = get_location(payload.locationId)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Location not found",
        )

    try:
        features = _features(item, payload.rainfall)
        result = ml_service.predict(features, simulated=True)

        _save_prediction(
            location_id=payload.locationId,
            probability=float(
                result["probability"]
            ),
            risk_level=str(
                result["riskLevel"]
            ),
            model_name=str(
                result["modelSource"]
            ),
            features=features,
        )

        return result

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )


@router.get("/status")
def model_status():
    return {
        "trained": ml_service.trained,
        "source": ml_service.model_source,
        "mode": (
            "trained"
            if ml_service.trained
            else "demo"
        ),
        "features": ml_service.feature_schema,
    }