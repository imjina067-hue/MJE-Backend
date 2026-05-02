from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.infrastructure.api.domain.entity.export_event import ExportEvent


@runtime_checkable
class ExportLogRepository(Protocol):
    async def save(self, event: ExportEvent) -> None: ...
