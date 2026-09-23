from datetime import datetime
from sqlalchemy import DateTime, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class Alert(Base):
    __tablename__ = "warnings"
    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[str] = mapped_column(String(80), index=True)
    risk_level: Mapped[str] = mapped_column(String(20))
    probability: Mapped[float] = mapped_column(Float)
    rainfall: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="active")
    recommended_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
