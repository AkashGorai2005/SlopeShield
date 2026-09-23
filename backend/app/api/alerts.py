from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database.database import engine
from app.services.monitoring_service import recommended_action

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _timestamp(value):
    return value.isoformat() if hasattr(value, "isoformat") else str(value) if value else None


@router.get("")
def alerts(status: str = "active"):
    query = text("""
        SELECT w.id, w.location_id, l.name, l.state, w.risk_level,
               w.probability, w.rainfall, w.status, w.created_at,
               w.recommended_action, w.resolved_at
        FROM warnings w
        JOIN locations l ON l.id = w.location_id
        WHERE (:status = 'all' OR w.status = :status)
        ORDER BY w.created_at DESC
    """)

    with engine.connect() as connection:
        return [
            {
                "id": f"w-{row['id']}",
                "locationId": row["location_id"],
                "location": f"{row['name']}, {row['state']}",
                "riskLevel": row["risk_level"],
                "rainfall": float(row["rainfall"] or 0),
                "probability": round(float(row["probability"] or 0) * 100),
                "change": 0,
                "timestamp": _timestamp(row["created_at"]),
                "status": row["status"],
                "recommendedAction": (
                    row["recommended_action"]
                    or recommended_action(row["risk_level"])
                ),
                "resolvedAt": _timestamp(row["resolved_at"]),
                "source": "PostgreSQL",
            }
            for row in connection.execute(query, {"status": status}).mappings()
        ]


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    # Accept both "w-19" and "19" for compatibility.
    raw_id = alert_id.strip()

    if raw_id.startswith("w-"):
        raw_id = raw_id[2:]

    try:
        alert_id_int = int(raw_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid alert ID. Expected format like w-19.",
        )

    with engine.begin() as connection:
        result = connection.execute(
            text("""
                UPDATE warnings
                SET status='resolved',
                    resolved_at=:resolved_at
                WHERE id=:id
                  AND status='active'
            """),
            {
                "id": alert_id_int,
                "resolved_at": datetime.now(timezone.utc).replace(tzinfo=None),
            },
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Active alert not found",
            )

    return {
        "id": f"w-{alert_id_int}",
        "status": "resolved",
    }