from __future__ import annotations

from datetime import datetime

from app.infrastructure.api.domain.entity.export_event import ExportEvent
from app.infrastructure.api.domain.value_object.event_name import EventName
from app.infrastructure.api.repository.export_log_repository import ExportLogRepository
from app.infrastructure.api.service.dto.request.track_export_event_request_dto import TrackExportEventRequestDto
from app.infrastructure.api.service.dto.response.track_export_event_response_dto import TrackExportEventResponseDto


class TrackExportEventUseCase:

    def __init__(self, repository: ExportLogRepository) -> None:
        self._repository = repository

    async def execute(self, dto: TrackExportEventRequestDto) -> TrackExportEventResponseDto:
        event_name = EventName(dto.event_name)

        event = ExportEvent(
            event_name=event_name.value,
            session_id=dto.session_id,
            page_path=dto.page_path,
            created_at=datetime.utcnow(),
        )

        try:
            await self._repository.save(event)
            return TrackExportEventResponseDto(success=True)
        except Exception:
            return TrackExportEventResponseDto(success=False, message="이벤트 저장에 실패했습니다.")
