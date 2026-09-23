from datetime import datetime
from pathlib import Path
import os
import sys
import time

import requests
from sqlalchemy import text


ROOT = Path(__file__).resolve().parents[1]


def load_backend_env():
    env_file = ROOT / ".env"

    if not env_file.exists():
        return

    for raw_line in env_file.read_text(
        encoding="utf-8"
    ).splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip()
        value = value.strip()

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]

        os.environ.setdefault(key, value)


load_backend_env()

sys.path.insert(0, str(ROOT))

from app.database.database import engine
from app.services.ml_service import ml_service


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

SOURCE = "Open-Meteo"

REQUEST_TIMEOUT = 60


def get_monitoring_locations():
    query = text(
        """
        SELECT
            id,
            name,
            state,
            latitude,
            longitude,
            elevation,
            slope,
            probability
        FROM locations
        WHERE id NOT LIKE 'event-%'
        ORDER BY id
        """
    )

    with engine.connect() as connection:
        return [
            dict(row)
            for row in connection.execute(query).mappings()
        ]


def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "precipitation,"
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m"
        ),
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "precipitation"
        ),
        "past_days": 7,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": "SLOPESHIELD-NER/1.0",
        },
    )

    response.raise_for_status()

    payload = response.json()

    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    precipitation = hourly.get("precipitation") or []

    if not times or not precipitation:
        raise RuntimeError(
            "Open-Meteo returned no hourly precipitation data."
        )

    current = payload.get("current") or {}
    current_time = current.get("time")

    if not current_time:
        current_time = times[-1]

    valid = []

    for timestamp, value in zip(times, precipitation):
        if value is None:
            continue

        if timestamp <= current_time:
            valid.append((timestamp, float(value)))

    if not valid:
        raise RuntimeError(
            "No hourly precipitation values up to current time."
        )

    last_24 = valid[-24:]
    last_168 = valid[-168:]

    rainfall_1h = last_24[-1][1]
    rainfall_24h = sum(
        value for _, value in last_24
    )
    rainfall_7d = sum(
        value for _, value in last_168
    )

    temperature = float(
        current.get("temperature_2m") or 0
    )

    humidity = float(
        current.get("relative_humidity_2m") or 0
    )

    wind_speed = float(
        current.get("wind_speed_10m") or 0
    )

    observed_at = datetime.fromisoformat(
        current_time.replace("Z", "+00:00")
    ).replace(tzinfo=None)

    return {
        "observed_at": observed_at,
        "rainfall_1h": max(
            0.0,
            rainfall_1h,
        ),
        "rainfall_24h": max(
            0.0,
            rainfall_24h,
        ),
        "rainfall_7d": max(
            0.0,
            rainfall_7d,
        ),
        "temperature": temperature,
        "humidity": max(
            0.0,
            min(100.0, humidity),
        ),
        "wind_speed": max(
            0.0,
            wind_speed,
        ),
    }


def save_observation(
    location_id,
    observation,
):
    update_query = text(
        """
        UPDATE rainfall_observations
        SET
            rainfall_1h = :rainfall_1h,
            rainfall_24h = :rainfall_24h,
            rainfall_7d = :rainfall_7d,
            source = :source,
            temperature = :temperature,
            humidity = :humidity,
            wind_speed = :wind_speed
        WHERE location_id = :location_id
          AND observed_at = :observed_at
        """
    )

    insert_query = text(
        """
        INSERT INTO rainfall_observations (
            location_id,
            observed_at,
            rainfall_1h,
            rainfall_24h,
            rainfall_7d,
            source,
            temperature,
            humidity,
            wind_speed
        )
        VALUES (
            :location_id,
            :observed_at,
            :rainfall_1h,
            :rainfall_24h,
            :rainfall_7d,
            :source,
            :temperature,
            :humidity,
            :wind_speed
        )
        """
    )

    values = {
        "location_id": location_id,
        "observed_at": observation["observed_at"],
        "rainfall_1h": observation["rainfall_1h"],
        "rainfall_24h": observation["rainfall_24h"],
        "rainfall_7d": observation["rainfall_7d"],
        "source": SOURCE,
        "temperature": observation["temperature"],
        "humidity": observation["humidity"],
        "wind_speed": observation["wind_speed"],
    }

    with engine.begin() as connection:
        result = connection.execute(
            update_query,
            values,
        )

        if result.rowcount == 0:
            connection.execute(
                insert_query,
                values,
            )


def recalculate_risk(
    location_id,
    observation,
    location,
):
    with engine.connect() as connection:
        historical_landslides = connection.execute(text("""
            SELECT COUNT(*) FROM historical_landslides h
            WHERE h.latitude IS NOT NULL AND h.longitude IS NOT NULL
              AND 6371.0 * 2 * ASIN(SQRT(
                POWER(SIN(RADIANS(h.latitude - :lat) / 2), 2) +
                COS(RADIANS(:lat)) * COS(RADIANS(h.latitude)) *
                POWER(SIN(RADIANS(h.longitude - :lon) / 2), 2)
              )) <= 25.0
        """), {"lat": float(location.get("latitude") or 0), "lon": float(location.get("longitude") or 0)}).scalar() or 0
    features = {
        "rainfall_24h": float(
            observation["rainfall_24h"]
            or 0
        ),
        "rainfall_7d": float(
            observation["rainfall_7d"]
            or 0
        ),
        "elevation": float(
            location.get("elevation")
            or 0
        ),
        "slope": float(
            location.get("slope")
            or 0
        ),
        "historical_landslides": int(historical_landslides),
    }

    result = ml_service.predict(
        features,
        simulated=False,
    )

    probability = float(
        result["probability"]
    )

    risk_level = str(
        result["riskLevel"]
    )

    model_source = str(
        result["modelSource"]
    )

    previous_probability = float(
        location.get("probability")
        or 0
    )

    if probability > previous_probability + 0.000001:
        trend = "increasing"
    elif probability < previous_probability - 0.000001:
        trend = "decreasing"
    else:
        trend = "stable"

    update_location_query = text(
        """
        UPDATE locations
        SET
            risk_level = :risk_level,
            probability = :probability,
            trend = :trend
        WHERE id = :location_id
        """
    )

    save_prediction_query = text(
        """
        INSERT INTO risk_predictions (
            location_id,
            probability,
            risk_level,
            model_name
        )
        VALUES (
            :location_id,
            :probability,
            :risk_level,
            :model_name
        )
        """
    )

    values = {
        "location_id": location_id,
        "probability": probability,
        "risk_level": risk_level,
        "trend": trend,
        "model_name": model_source,
    }

    with engine.begin() as connection:
        update_result = connection.execute(
            update_location_query,
            values,
        )

        if update_result.rowcount == 0:
            raise RuntimeError(
                f"Location '{location_id}' "
                "was not found while updating risk."
            )

        connection.execute(
            save_prediction_query,
            values,
        )

    return {
        "probability": probability,
        "riskLevel": risk_level,
        "modelSource": model_source,
        "trend": trend,
    }


def main():
    locations = get_monitoring_locations()

    if not locations:
        raise SystemExit(
            "No named monitoring locations were found."
        )

    if not ml_service.trained:
        raise SystemExit(
            "Trained ML model is unavailable. "
            "Automatic risk recalculation cannot continue."
        )

    print(
        f"Found {len(locations)} named monitoring locations."
    )
    print(
        "Historical event-* rainfall observations "
        "will not be modified."
    )
    print(
        f"ML model: {ml_service.model_source}"
    )
    print()

    success = 0
    failed = 0
    risk_updated = 0

    for location in locations:
        location_id = location["id"]
        name = location["name"]

        print(
            f"Updating {name} ({location_id})...",
            end=" ",
            flush=True,
        )

        try:
            observation = fetch_weather(
                float(location["latitude"]),
                float(location["longitude"]),
            )

            save_observation(
                location_id,
                observation,
            )

            risk = recalculate_risk(
                location_id,
                observation,
                location,
            )

            print(
                "OK | "
                f"24h={observation['rainfall_24h']:.1f} mm | "
                f"7d={observation['rainfall_7d']:.1f} mm | "
                f"risk={risk['riskLevel']} | "
                f"probability={risk['probability']:.3f} | "
                f"trend={risk['trend']} | "
                f"model={risk['modelSource']} | "
                f"time={observation['observed_at']}"
            )

            success += 1
            risk_updated += 1

        except Exception as exc:
            print(
                f"FAILED | {exc}"
            )
            failed += 1

        time.sleep(0.25)

    print()
    print(
        "Monitoring weather and ML risk update complete."
    )
    print(
        f"Successful: {success}"
    )
    print(
        f"Failed:     {failed}"
    )
    print(
        f"Risk updated: {risk_updated}"
    )


if __name__ == "__main__":
    main()