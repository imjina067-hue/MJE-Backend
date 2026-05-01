from datetime import datetime

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class EmailLogOrm(Base):
    __tablename__ = "email_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    course_id: Mapped[str] = mapped_column(String(36), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DATETIME(fsp=6), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DATETIME(fsp=6), nullable=True)
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)
