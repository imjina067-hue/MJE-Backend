from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.api.domain.entity.export_event import ExportEvent
from app.infrastructure.api.repository.mapper.export_log_mapper import ExportLogMapper


class ExportLogRepositoryImpl:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: ExportEvent) -> None:
        orm = ExportLogMapper.to_orm(event)
        self._session.add(orm)
        await self._session.flush()
