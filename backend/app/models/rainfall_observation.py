from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[str] = mapped_column(String(80), index=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    rainfall_1h: Mapped[float] = mapped_column(Float, default=0.0)
    rainfall_24h: Mapped[float] = mapped_column(Float, default=0.0)
    rainfall_7d: Mapped[float] = mapped_column(Float, default=0.0)
    source: Mapped[str] = mapped_column(String(80), default="Open-Meteo")
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, default=0.0)
    wind_speed: Mapped[float] = mapped_column(Float, default=0.0)
