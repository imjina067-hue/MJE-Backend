from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domains.home.domain.entity.event import Event


@runtime_checkable
class EventRepository(Protocol):
    async def save(self, event: Event) -> None: ...
