from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base

class Sensor(Base):
    __tablename__ = "sensors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="disabled")
