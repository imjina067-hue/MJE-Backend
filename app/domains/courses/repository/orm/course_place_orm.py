from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class CoursePlaceOrm(Base):
    __tablename__ = "course_places"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id: Mapped[str] = mapped_column(String(36), nullable=False)
    visit_order: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    route_distance_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_transport: Mapped[str | None] = mapped_column(String(20), nullable=True)
    route_polyline: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(fsp=6), nullable=False)
