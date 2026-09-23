from __future__ import annotations

import math

import threading

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime

import requests

from sqlalchemy import text

from app.database.database import engine

from app.config import get_settings

from app.services.ml_service import ml_service

from app.services.imd_rainfall_service import fetch_rainfall
from app.services.telegram_service import send_telegram_alert

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

SOURCE = "IMD + Open-Meteo fallback"

REQUEST_TIMEOUT = 15

_cycle_lock = threading.Lock()

_monitoring_state = {

    "enabled": True,

    "running": False,

    "lastStartedAt": None,

    "lastCompletedAt": None,

    "lastResult": None,

    "lastError": None,

}

def monitoring_status() -> dict:

    return dict(_monitoring_state)

def recommended_action(risk_level: str) -> str:

    return {

        "critical": "Immediate attention: inspect the area and follow local authority guidance.",

        "high": "Issue a warning and increase monitoring of the location.",

    }.get(risk_level, "Continue routine monitoring.")

def _fetch_weather(latitude: float, longitude: float) -> dict:

    response = requests.get(

        OPEN_METEO_URL,

        params={

            "latitude": latitude,

            "longitude": longitude,

            "hourly": "precipitation,temperature_2m,relative_humidity_2m,wind_speed_10m",

            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",

            "past_days": 7,

            "forecast_days": 1,

            "timezone": "UTC",

        },

        timeout=REQUEST_TIMEOUT,

        headers={"User-Agent": "SLOPESHIELD-NER/1.0"},

    )

    response.raise_for_status()

    payload = response.json()

    hourly = payload.get("hourly") or {}

    times = hourly.get("time") or []

    precipitation = hourly.get("precipitation") or []

    current = payload.get("current") or {}

    current_time = current.get("time") or (times[-1] if times else None)

    valid = [

        (timestamp, float(value or 0))

        for timestamp, value in zip(times, precipitation)

        if timestamp <= current_time

    ] if current_time else []

    if not valid:

        raise RuntimeError("Open-Meteo returned no hourly precipitation data.")

    observed_at = datetime.fromisoformat(valid[-1][0].replace("Z", "+00:00")).replace(tzinfo=None)

    return {

        "observed_at": observed_at,

        "rainfall_1h": max(0.0, valid[-1][1]),

        "rainfall_24h": max(0.0, sum(value for _, value in valid[-24:])),

        "rainfall_7d": max(0.0, sum(value for _, value in valid[-168:])),

        "temperature": float(current.get("temperature_2m") or 0),

        "humidity": max(0.0, min(100.0, float(current.get("relative_humidity_2m") or 0))),

        "wind_speed": max(0.0, float(current.get("wind_speed_10m") or 0)),

    }

def _historical_count(connection, latitude: float, longitude: float) -> int:

    rows = connection.execute(text("SELECT latitude, longitude FROM historical_landslides WHERE latitude IS NOT NULL AND longitude IS NOT NULL")).mappings()

    count = 0

    for row in rows:

        lat_delta = math.radians(float(row["latitude"]) - latitude)

        lon_delta = math.radians(float(row["longitude"]) - longitude)

        a = math.sin(lat_delta / 2) ** 2 + math.cos(math.radians(latitude)) * math.cos(math.radians(float(row["latitude"]))) * math.sin(lon_delta / 2) ** 2

        if 6371.0 * 2 * math.asin(min(1.0, math.sqrt(a))) <= 25.0:

            count += 1

    return count

def _fetch_location_weather(location: dict) -> tuple[dict, dict | None, str | None]:

    # Prefer official IMD rainfall. Fall back to Open-Meteo if IMD is

    # unavailable for this location or temporarily fails.

    try:

        observation = fetch_rainfall(str(location["name"]))

        return location, observation, None

    except Exception as imd_exc:

        try:

            observation = _fetch_weather(

                float(location["latitude"]),

                float(location["longitude"]),

            )

            observation["source"] = "Open-Meteo (fallback)"

            observation["source_detail"] = f"IMD unavailable: {imd_exc}"

            return location, observation, None

        except Exception as fallback_exc:

            return location, None, (

                f"IMD error: {imd_exc}; Open-Meteo fallback error: {fallback_exc}"

            )

def _save_observation(connection, location_id: str, observation: dict) -> None:

    values = {"location_id": location_id, "source": observation.get("source", SOURCE), **observation}

    updated = connection.execute(text("""

        UPDATE rainfall_observations

        SET rainfall_1h=:rainfall_1h, rainfall_24h=:rainfall_24h, rainfall_7d=:rainfall_7d,

            source=:source, temperature=:temperature, humidity=:humidity, wind_speed=:wind_speed

        WHERE location_id=:location_id AND observed_at=:observed_at

    """), values)

    if updated.rowcount == 0:

        connection.execute(text("""

            INSERT INTO rainfall_observations

            (location_id, observed_at, rainfall_1h, rainfall_24h, rainfall_7d, source, temperature, humidity, wind_speed)

            VALUES (:location_id, :observed_at, :rainfall_1h, :rainfall_24h, :rainfall_7d, :source, :temperature, :humidity, :wind_speed)

        """), values)

def _save_prediction_and_alert(connection, location: dict, observation: dict, result: dict, historical_landslides: int) -> bool:

    probability = float(result["probability"])

    risk_level = str(result["riskLevel"])

    previous = float(location.get("probability") or 0)

    trend = "increasing" if probability > previous + 0.000001 else "decreasing" if probability < previous - 0.000001 else "stable"

    connection.execute(text("""

        UPDATE locations

        SET risk_level=:risk_level, probability=:probability, rainfall=:rainfall, trend=:trend,

            historical_landslides=:historical_landslides

        WHERE id=:location_id

    """), {"location_id": location["id"], "risk_level": risk_level, "probability": probability, "rainfall": observation["rainfall_24h"], "trend": trend, "historical_landslides": historical_landslides})

    connection.execute(text("""

        INSERT INTO risk_predictions

        (location_id, probability, risk_level, model_name, rainfall_24h, rainfall_7d,

         elevation, slope, historical_landslides, created_at)

        VALUES

        (:location_id, :probability, :risk_level, :model_name, :rainfall_24h, :rainfall_7d,

         :elevation, :slope, :historical_landslides, CURRENT_TIMESTAMP)

    """), {

        "location_id": location["id"],

        "probability": probability,

        "risk_level": risk_level,

        "model_name": result["modelSource"],

        "rainfall_24h": observation["rainfall_24h"],

        "rainfall_7d": observation["rainfall_7d"],

        "elevation": location["elevation"],

        "slope": location["slope"],

        "historical_landslides": historical_landslides,

    })

    active = connection.execute(text("SELECT id FROM warnings WHERE location_id=:location_id AND status='active' AND risk_level=:risk_level LIMIT 1"), {"location_id": location["id"], "risk_level": risk_level}).first()

    if risk_level in {"high", "critical"}:

        alert_values = {
            "location_id": location["id"],
            "risk_level": risk_level,
            "probability": probability,
            "rainfall": observation["rainfall_24h"],
            "recommended_action": recommended_action(risk_level),
        }

        if active:
            connection.execute(
                text("UPDATE warnings SET probability=:probability, rainfall=:rainfall, recommended_action=:recommended_action WHERE id=:id"),
                {**alert_values, "id": active[0]},
            )

            # Existing alert: do not send another Telegram notification.
            return False

        connection.execute(
            text("INSERT INTO warnings (location_id, risk_level, probability, rainfall, recommended_action, status, created_at) VALUES (:location_id, :risk_level, :probability, :rainfall, :recommended_action, 'active', CURRENT_TIMESTAMP)"),
            alert_values,
        )

        # New High/Critical alert: send one Telegram notification.
        return True

    connection.execute(
        text("UPDATE warnings SET status='resolved', resolved_at=CURRENT_TIMESTAMP WHERE location_id=:location_id AND status='active'"),
        {"location_id": location["id"]},
    )

    return False

def run_monitoring_cycle() -> dict:

    if not _cycle_lock.acquire(blocking=False):

        raise RuntimeError("A monitoring cycle is already running.")

    started_at = datetime.utcnow()

    _monitoring_state.update({

        "running": True,

        "lastStartedAt": started_at.isoformat(),

        "lastError": None,

    })

    try:

        return _run_monitoring_cycle()

    except Exception as exc:

        _monitoring_state["lastError"] = str(exc)

        raise

    finally:

        _monitoring_state["running"] = False

        _monitoring_state["lastCompletedAt"] = datetime.utcnow().isoformat()

        _cycle_lock.release()

def _run_monitoring_cycle() -> dict:

    if not ml_service.trained:

        raise RuntimeError("Trained ML model is unavailable. Run the real-data pipeline first.")

    with engine.connect() as connection:

        locations = [dict(row) for row in connection.execute(text("""

            SELECT id, name, state, latitude, longitude, elevation, slope, historical_landslides, probability

            FROM locations WHERE id NOT LIKE 'event-%' ORDER BY id

        """ )).mappings()]

    fetched = {}

    failures = []

    with ThreadPoolExecutor(max_workers=min(8, max(1, len(locations)))) as executor:

        futures = [executor.submit(_fetch_location_weather, location) for location in locations]

        for future in as_completed(futures):

            location, observation, error = future.result()

            if error:

                failures.append({"locationId": location["id"], "location": location["name"], "error": error})

            else:

                fetched[location["id"]] = (location, observation)

    results = []
    telegram_alerts = []

    with engine.begin() as connection:
        for location in locations:
            item = fetched.get(location["id"])

            if not item:
                continue

            location, observation = item

            try:
                _save_observation(
                    connection,
                    location["id"],
                    observation,
                )

                historical_landslides = _historical_count(
                    connection,
                    float(location["latitude"]),
                    float(location["longitude"]),
                )

                prediction = ml_service.predict(
                    {
                        "rainfall_24h": observation["rainfall_24h"],
                        "rainfall_7d": observation["rainfall_7d"],
                        "elevation": location["elevation"],
                        "slope": location["slope"],
                        "historical_landslides": historical_landslides,
                    }
                )

                new_alert = _save_prediction_and_alert(
                    connection,
                    location,
                    observation,
                    prediction,
                    historical_landslides,
                )

                if new_alert:
                    telegram_alerts.append(
                        {
                            "location": f'{location["name"]}, {location["state"]}',
                            "risk_level": prediction["riskLevel"],
                            "probability": prediction["probability"],
                            "rainfall": observation["rainfall_24h"],
                            "recommended_action": recommended_action(
                                prediction["riskLevel"]
                            ),
                        }
                    )

                results.append(
                    {
                        "locationId": location["id"],
                        "location": location["name"],
                        "rainfall24h": observation["rainfall_24h"],
                        "rainfall7d": observation["rainfall_7d"],
                        "riskLevel": prediction["riskLevel"],
                        "probability": prediction["probability"],
                        "modelSource": prediction["modelSource"],
                        "observedAt": observation["observed_at"].isoformat(),
                        "source": observation.get("source", SOURCE),
                    }
                )

            except Exception as exc:
                failures.append(
                    {
                        "locationId": location["id"],
                        "location": location["name"],
                        "error": str(exc),
                    }
                )

    # Send Telegram notifications only after the database transaction succeeds.
    for alert in telegram_alerts:
        send_telegram_alert(
            location=alert["location"],
            risk_level=alert["risk_level"],
            probability=alert["probability"],
            rainfall=alert["rainfall"],
            recommended_action=alert["recommended_action"],
        )

    result = {"source": SOURCE, "modelSource": ml_service.model_source, "updated": len(results), "failed": len(failures), "results": results, "failures": failures}

    _monitoring_state["lastResult"] = {

        "updated": result["updated"],

        "failed": result["failed"],

        "source": result["source"],

        "modelSource": result["modelSource"],

    }

    return result

