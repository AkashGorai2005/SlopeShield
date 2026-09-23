from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.database.database import engine
from app.config import get_settings


ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

FEATURE_FILE = PROCESSED / "location_features.csv"
HIST_FILE = RAW / "ner_landslides.csv"
DATABASE_LABEL = "PostgreSQL" if get_settings().database_url.startswith("postgres") else "SQLite"


REFERENCE_LOCATIONS = [
    (
        "aizawl",
        "Aizawl",
        "Mizoram",
        23.7271,
        92.7176,
        214,
        38,
        1132,
        "Urban settlement on steep slopes",
        "Barail sandstone & shale",
    ),
    (
        "shillong",
        "Shillong",
        "Meghalaya",
        25.5788,
        91.8933,
        186,
        27,
        1496,
        "Pine forest & built-up",
        "Shillong group quartzite",
    ),
    (
        "cherrapunji",
        "Cherrapunji (Sohra)",
        "Meghalaya",
        25.3,
        91.7,
        342,
        44,
        1430,
        "Grassland & bare escarpment",
        "Sandstone over gneiss",
    ),
    (
        "gangtok",
        "Gangtok",
        "Sikkim",
        27.3314,
        88.6138,
        158,
        33,
        1650,
        "Terraced settlement",
        "Daling phyllite",
    ),
    (
        "itanagar",
        "Itanagar",
        "Arunachal Pradesh",
        27.0844,
        93.6053,
        121,
        21,
        617,
        "Subtropical broadleaf forest",
        "Siwalik sandstone",
    ),
    (
        "tawang",
        "Tawang",
        "Arunachal Pradesh",
        27.5861,
        91.8594,
        96,
        36,
        3048,
        "Alpine scrub",
        "Gneissic complex",
    ),
    (
        "kohima",
        "Kohima",
        "Nagaland",
        25.6751,
        94.1086,
        149,
        31,
        1444,
        "Mixed forest & settlement",
        "Disang shale",
    ),
    (
        "dimapur",
        "Dimapur",
        "Nagaland",
        25.9063,
        93.7276,
        62,
        5,
        145,
        "Alluvial plain, cropland",
        "Recent alluvium",
    ),
    (
        "imphal",
        "Imphal",
        "Manipur",
        24.817,
        93.9368,
        74,
        7,
        786,
        "Valley cropland",
        "Lacustrine deposits",
    ),
    (
        "churachandpur",
        "Churachandpur",
        "Manipur",
        24.3333,
        93.6833,
        133,
        24,
        914,
        "Jhum cultivation slopes",
        "Disang flysch",
    ),
    (
        "haflong",
        "Haflong",
        "Assam",
        25.1667,
        93.0167,
        197,
        35,
        680,
        "Cut slopes along rail corridor",
        "Barail group sandstone",
    ),
    (
        "guwahati",
        "Guwahati",
        "Assam",
        26.1445,
        91.7362,
        108,
        18,
        55,
        "Urban hillocks",
        "Weathered granite gneiss",
    ),
    (
        "lunglei",
        "Lunglei",
        "Mizoram",
        22.8879,
        92.7346,
        171,
        32,
        1133,
        "Bamboo forest & settlement",
        "Bhuban formation",
    ),
    (
        "agartala",
        "Agartala",
        "Tripura",
        23.8315,
        91.2868,
        58,
        4,
        16,
        "Plain, urban",
        "Dupitila sandstone",
    ),
    (
        "pelling",
        "Pelling",
        "Sikkim",
        27.3,
        88.2167,
        164,
        37,
        2150,
        "Temperate forest",
        "Central crystalline gneiss",
    ),
]


def _probability(
    rainfall: float,
    slope: float,
    elevation: float,
) -> float:
    import math

    z = (
        -4.2
        + 0.010 * rainfall
        + 0.045 * slope
        + 0.00015 * elevation
    )

    return 1 / (1 + math.exp(-z))


def _risk(probability: float) -> str:
    if probability >= 0.75:
        return "critical"

    if probability >= 0.55:
        return "high"

    if probability >= 0.30:
        return "moderate"

    return "low"


def _reference():
    rows = []

    for (
        location_id,
        name,
        state,
        latitude,
        longitude,
        rainfall,
        slope,
        elevation,
        land_cover,
        geology,
    ) in REFERENCE_LOCATIONS:

        probability = _probability(
            rainfall,
            slope,
            elevation,
        )

        rows.append(
            {
                "id": location_id,
                "name": name,
                "state": state,
                "latitude": latitude,
                "longitude": longitude,
                "riskLevel": _risk(probability),
                "probability": round(
                    probability,
                    4,
                ),
                "rainfall": rainfall,
                "rainfall7d": 0,
                "slope": slope,
                "elevation": elevation,
                "landCover": land_cover,
                "geology": geology,
                "historicalLandslides": 0,
                "trend": "stable",
                "modelSource": "reference-only",
                "dataMode": "reference",
            }
        )

    return rows


def _from_features():
    if not FEATURE_FILE.exists():
        return []

    try:
        df = pd.read_csv(FEATURE_FILE)
    except Exception:
        return []

    if df.empty or not {
        "latitude",
        "longitude",
    }.issubset(df.columns):
        return []

    rows = []

    for index, row in df.iterrows():
        try:
            latitude = float(row.latitude)
            longitude = float(row.longitude)
        except Exception:
            continue

        if row.get("target", 0) != 1:
            continue

        name = str(
            row.get("place")
            or f"NER event {index + 1}"
        )

        probability = float(
            row.get(
                "probability",
                row.get(
                    "target_probability",
                    0.5,
                ),
            )
            or 0.5
        )

        rows.append(
            {
                "id": f"event-{index + 1}",
                "name": name,
                "state": str(
                    row.get("state")
                    or "Northeast India"
                ),
                "latitude": latitude,
                "longitude": longitude,
                "riskLevel": _risk(probability),
                "probability": round(
                    probability,
                    4,
                ),
                "rainfall": float(
                    row.get(
                        "rainfall_24h",
                        0,
                    )
                    or 0
                ),
                "rainfall7d": float(
                    row.get(
                        "rainfall_7d",
                        0,
                    )
                    or 0
                ),
                "slope": float(
                    row.get(
                        "slope",
                        0,
                    )
                    or 0
                ),
                "elevation": float(
                    row.get(
                        "elevation",
                        0,
                    )
                    or 0
                ),
                "landCover": str(
                    row.get(
                        "land_cover",
                        "Unavailable",
                    )
                ),
                "geology": str(
                    row.get(
                        "geology",
                        "Unavailable",
                    )
                ),
                "historicalLandslides": int(
                    row.get(
                        "historical_landslides",
                        1,
                    )
                    or 1
                ),
                "trend": "observed",
                "modelSource": str(
                    row.get(
                        "model_source",
                        "real-source",
                    )
                ),
                "dataMode": "real-source",
            }
        )

    return rows[:500]


def get_locations():
    query = text(
        """
        SELECT
            l.id,
            l.name,
            l.state,
            l.latitude,
            l.longitude,
            l.elevation,
            l.slope,
            l.land_cover,
            l.geology,
            l.historical_landslides,
            l.risk_level,
            l.probability,
            COALESCE(
                (
                    SELECT rainfall_24h
                    FROM rainfall_observations ro
                    WHERE ro.location_id = l.id
                    ORDER BY ro.observed_at DESC
                    LIMIT 1
                ),
                l.rainfall,
                0
            ) AS rainfall,
            COALESCE(
                (
                    SELECT rainfall_7d
                    FROM rainfall_observations ro
                    WHERE ro.location_id = l.id
                    ORDER BY ro.observed_at DESC
                    LIMIT 1
                ),
                0
            ) AS rainfall7d,
            l.trend
        FROM locations l
        WHERE l.id NOT LIKE 'event-%'
        ORDER BY l.id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)

        rows = []

        for row in result.mappings():
            rows.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "state": row["state"],
                    "latitude": float(
                        row["latitude"]
                    ),
                    "longitude": float(
                        row["longitude"]
                    ),
                    "riskLevel": row[
                        "risk_level"
                    ],
                    "probability": float(
                        row["probability"]
                        or 0
                    ),
                    "rainfall": float(
                        row["rainfall"]
                        or 0
                    ),
                    "rainfall7d": float(
                        row["rainfall7d"]
                        or 0
                    ),
                    "slope": float(
                        row["slope"]
                        or 0
                    ),
                    "elevation": float(
                        row["elevation"]
                        or 0
                    ),
                    "landCover": row[
                        "land_cover"
                    ],
                    "geology": row[
                        "geology"
                    ],
                    "historicalLandslides": int(
                        row[
                            "historical_landslides"
                        ]
                        or 0
                    ),
                    "trend": row["trend"],
                    "modelSource": DATABASE_LABEL,
                    "dataMode": "database",
                }
            )

        return rows


def get_location(location_id):
    locations = get_locations()

    for location in locations:
        if location["id"] == location_id:
            return location

    return None


def _first_value(row, keys, default=None):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]

    return default

def get_historical():
    query = text(
        """
        SELECT
            id,
            latitude,
            longitude,
            date,
            year,
            place,
            state,
            severity,
            source,
            description
        FROM historical_landslides
        ORDER BY date DESC NULLS LAST, id
        """
    )

    try:
        with engine.connect() as connection:
            result = connection.execute(query)

            points = []

            for row in result.mappings():
                latitude = row.get("latitude")
                longitude = row.get("longitude")

                if latitude is None or longitude is None:
                    continue

                observed_date = row.get("date")

                if hasattr(observed_date, "isoformat"):
                    observed_date = observed_date.isoformat()

                points.append(
                    {
                        "id": row.get("id"),
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                        "date": observed_date,
                        "year": row.get("year"),
                        "place": row.get("place"),
                        "state": row.get("state"),
                        "severity": row.get("severity"),
                        "source": row.get("source"),
                        "description": row.get("description"),
                    }
                )

            return {
                "points": points,
                "count": len(points),
                "source": DATABASE_LABEL,
            }

    except Exception as exc:
        print(f"Historical data error: {exc}")
        return {
            "points": [],
            "count": 0,
            "source": DATABASE_LABEL,
            "error": str(exc),
        }


def data_status():
    feature_table_exists = (
        FEATURE_FILE.exists()
    )

    historical_file_exists = HIST_FILE.exists()
    historical_database_count = 0

    try:
        with engine.connect() as connection:
            historical_database_count = connection.execute(
                text("SELECT COUNT(*) FROM historical_landslides")
            ).scalar() or 0
    except Exception:
        historical_database_count = 0

    return {
        "mode": "database",
        "featureTable": feature_table_exists,
        "historicalInventory": historical_file_exists,
        "historicalDataAvailable": bool(
            historical_file_exists or historical_database_count
        ),
        "historicalDatabaseCount": int(historical_database_count),
        "featureFile": str(
            FEATURE_FILE
        ),
        "historicalFile": str(
            HIST_FILE
        ),
        "generatedAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }


def get_risk():
    locations = get_locations()

    levels = [
        "low",
        "moderate",
        "high",
        "critical",
    ]

    distribution = [
        {
            "level": level,
            "count": sum(
                location["riskLevel"]
                == level
                for location in locations
            ),
        }
        for level in levels
    ]

    regional = {}

    for location in locations:
        regional.setdefault(
            location["state"],
            [],
        ).append(
            location["probability"]
        )

    regional_rows = [
        {
            "state": state,
            "region": state,
            "risk": round(
                sum(values)
                / len(values),
                3,
            ),
            "locations": len(values),
            "rainfall": round(sum(location["rainfall"] for location in locations if location["state"] == state) / len(values), 2),
        }
        for state, values in sorted(
            regional.items()
        )
    ]

    now = datetime.now(timezone.utc).isoformat()
    trend = [{
        "day": now[:16].replace("T", " "),
        **{level: sum(location["riskLevel"] == level for location in locations) for level in levels},
    }]

       # Use the trained model's feature importance instead of comparing
    # raw feature magnitudes. Raw values are not directly comparable
    # across features (e.g. elevation is measured in metres while
    # slope is measured in degrees).
    factors = []

    try:
        from app.services.ml_service import ml_service

        model = ml_service.model
        model = model.get("model") if isinstance(model, dict) else model
        importances = getattr(model, "feature_importances_", None)

        if importances is not None:
            feature_names = {
                "rainfall_24h": "Rainfall 24h",
                "rainfall_7d": "Rainfall 7d",
                "elevation": "Elevation",
                "slope": "Slope",
                "historical_landslides": "Historical events",
            }

            total_importance = sum(float(value) for value in importances)

            if total_importance > 0:
                factors = [
                    {
                        "factor": feature_names[feature],
                        "weight": round(
                            float(importance) / total_importance * 100,
                            1,
                        ),
                    }
                    for feature, importance in zip(
                        ml_service.feature_schema,
                        importances,
                    )
                ]

    except Exception as exc:
        print(f"Feature importance unavailable: {exc}")

    if not factors:
        factors = [
            {
                "factor": "Model feature importance",
                "weight": 0,
            }
        ]

    recent_changes = [
        {
            "id": location["id"],
            "location": location["name"],
            "from": "low" if location["trend"] == "increasing" else location["riskLevel"],
            "to": location["riskLevel"],
            "at": now,
        }
        for location in locations
        if location["trend"] in {"increasing", "decreasing"}
    ]

    return {
        "distribution": distribution,
        "trend": trend,
        "factors": factors,
        "regional": regional_rows,
        "recentChanges": recent_changes,
    }


def get_rainfall():
    query = text(
        """
        SELECT
            ro.location_id,
            l.name,
            l.risk_level,
            l.probability,
            observed_at,
            rainfall_1h,
            rainfall_24h,
            rainfall_7d,
            source
        FROM rainfall_observations ro
        JOIN locations l ON l.id = ro.location_id
        ORDER BY observed_at
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query)

        series = []

        for row in result.mappings():
            observed_at = row[
                "observed_at"
            ]

            if isinstance(
                observed_at,
                datetime,
            ):
                observed_at = (
                    observed_at.isoformat()
                )
            else:
                observed_at = str(
                    observed_at
                )

            series.append(
                {
                    "locationId": str(
                        row["location_id"]
                    ),
                    "day": str(row["observed_at"])[:16],
                    "location": row["name"],
                    "risk": float(row["probability"] or 0),
                    "rainfall": float(row["rainfall_24h"] or 0),
                    "observedAt": observed_at,
                    "rainfall1h": float(
                        row["rainfall_1h"]
                        or 0
                    ),
                    "rainfall24h": float(
                        row["rainfall_24h"]
                        or 0
                    ),
                    "rainfall7d": float(
                        row["rainfall_7d"]
                        or 0
                    ),
                    "source": str(
                        row["source"]
                        or "Database"
                    ),
                }
            )

    last24 = max(
        (
            item["rainfall24h"]
            for item in series
        ),
        default=None,
    )

    last7d = max(
        (
            item["rainfall7d"]
            for item in series
        ),
        default=None,
    )

    return {
        "series": series,
        "status": {
            "headline": "Source-aware rainfall",
            "last24h": last24,
            "last7d": last7d,
            "intensity": (
                "Calculated per monitored point"
            ),
            "note": (
                "Rainfall values are loaded "
                f"from {DATABASE_LABEL} rainfall "
                "observations."
            ),
        },
    }


def get_summary():
    locations = get_locations()

    historical = get_historical()["points"]

    return {
        "monitoredAreas": len(
            locations
        ),
        "attentionAreas": sum(
            location["riskLevel"]
            in {
                "high",
                "critical",
            }
            for location in locations
        ),
        "increasing": sum(
            location["trend"]
            == "increasing"
            for location in locations
        ),
        "historicalEvents": len(
            historical
        ),
        "dataStatus": data_status(),
    }