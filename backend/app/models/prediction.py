from datetime import datetime
from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class Prediction(Base):
    __tablename__ = "risk_predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[str] = mapped_column(String(80), index=True)
    probability: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(20))
    model_name: Mapped[str] = mapped_column(String(80))
    rainfall_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    rainfall_7d: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation: Mapped[float | None] = mapped_column(Float, nullable=True)
    slope: Mapped[float | None] = mapped_column(Float, nullable=True)
    historical_landslides: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
