from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config.settings import get_settings


def _build_url() -> URL | None:
    s = get_settings()
    if not all([s.MYSQL_HOST, s.MYSQL_USER, s.MYSQL_PASSWORD, s.MYSQL_SCHEMA]):
        return None
    return URL.create(
        drivername="mysql+aiomysql",
        username=s.MYSQL_USER,
        password=s.MYSQL_PASSWORD,
        host=s.MYSQL_HOST,
        port=s.MYSQL_PORT,
        database=s.MYSQL_SCHEMA,
    )


_db_url = _build_url()
_engine = create_async_engine(_db_url, echo=False, pool_pre_ping=True) if _db_url else None
_session_factory: async_sessionmaker[AsyncSession] | None = (
    async_sessionmaker(_engine, expire_on_commit=False) if _engine else None
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        raise RuntimeError("데이터베이스가 설정되지 않았습니다. MYSQL_* 환경 변수를 확인해주세요.")
    async with _session_factory() as session:
        async with session.begin():
            yield session
