from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.home.domain.entity.event import Event
from app.domains.home.repository.mapper.event_mapper import EventMapper


class EventRepositoryImpl:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: Event) -> None:
        orm = EventMapper.to_orm(event)
        self._session.add(orm)
        await self._session.flush()
