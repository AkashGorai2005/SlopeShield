from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings
from pathlib import Path
import pandas as pd

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=NullPool,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import user, location, sensor, prediction, alert, historical_landslide  # noqa: F401
    from app.models.location import Location
    from app.models.historical_landslide import HistoricalLandslide
    from app.models.alert import Alert
    from app.services.data_service import REFERENCE_LOCATIONS

    Base.metadata.create_all(bind=engine)

    prediction_columns = {
        column["name"]
        for column in inspect(engine).get_columns("risk_predictions")
    }

    feature_columns = {
        "rainfall_24h": "FLOAT",
        "rainfall_7d": "FLOAT",
        "elevation": "FLOAT",
        "slope": "FLOAT",
        "historical_landslides": "INTEGER",
    }

    with engine.begin() as connection:
        for name, data_type in feature_columns.items():
            if name not in prediction_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE risk_predictions ADD COLUMN {name} {data_type}"
                    )
                )

    alert_columns = {
        column["name"]
        for column in inspect(engine).get_columns("warnings")
    }

    with engine.begin() as connection:
        for name, data_type in {
            "recommended_action": "VARCHAR(255)",
            "resolved_at": "TIMESTAMP",
        }.items():
            if name not in alert_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE warnings ADD COLUMN {name} {data_type}"
                    )
                )

    with SessionLocal.begin() as session:
        if session.query(Location).count() == 0:
            session.add_all(
                Location(
                    id=location_id,
                    name=name,
                    state=state,
                    latitude=latitude,
                    longitude=longitude,
                    rainfall=0,
                    slope=slope,
                    elevation=elevation,
                    land_cover=land_cover,
                    geology=geology,
                )
                for (
                    location_id,
                    name,
                    state,
                    latitude,
                    longitude,
                    _rainfall,
                    slope,
                    elevation,
                    land_cover,
                    geology,
                ) in REFERENCE_LOCATIONS
            )

        if session.query(HistoricalLandslide).count() == 0:
            source = (
                Path(__file__).resolve().parents[2]
                / "data"
                / "raw"
                / "nasa_global_landslides.csv"
            )

            if source.exists():
                frame = pd.read_csv(source)

                states = {
                    "Assam",
                    "Arunachal Pradesh",
                    "Arunāchal Pradesh",
                    "Manipur",
                    "Meghalaya",
                    "Meghālaya",
                    "Mizoram",
                    "Nagaland",
                    "Nāgāland",
                    "Sikkim",
                    "Tripura",
                }

                triggers = {
                    "downpour",
                    "rain",
                    "continuous_rain",
                    "monsoon",
                    "tropical_cyclone",
                }

                frame = frame[
                    (frame["country_name"].astype(str).str.strip() == "India")
                    & frame["admin_division_name"]
                    .astype(str)
                    .str.strip()
                    .isin(states)
                    & frame["landslide_trigger"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(triggers)
                ].dropna(subset=["latitude", "longitude"]).head(250)

                records = []

                for _, row in frame.iterrows():
                    event_date = pd.to_datetime(
                        row.get("event_date"),
                        errors="coerce",
                    )

                    records.append(
                        HistoricalLandslide(
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            date=(
                                event_date.date()
                                if not pd.isna(event_date)
                                else None
                            ),
                            year=(
                                int(event_date.year)
                                if not pd.isna(event_date)
                                else None
                            ),
                            place=str(
                                row.get("location_description")
                                or row.get("gazeteer_closest_point")
                                or "Northeast India"
                            ),
                            state=str(
                                row.get("admin_division_name")
                                or "Northeast India"
                            ),
                            severity=str(
                                row.get("landslide_size")
                                or "Recorded event"
                            ),
                            source="NASA Global Landslide Catalog",
                            description=str(
                                row.get("event_description")
                                or "NASA Global Landslide Catalog event"
                            ),
                        )
                    )

                session.add_all(records)