from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class RecommendationRequestOrm(Base):
    __tablename__ = "recommendation_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(36), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_hours: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    transport_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(fsp=6), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(fsp=6), nullable=True)
