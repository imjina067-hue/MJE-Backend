from __future__ import annotations

from datetime import datetime

from app.domains.courses.domain.entity.event import Event
from app.domains.courses.domain.value_object.event_name import EventName
from app.domains.courses.repository.event_repository import EventRepository
from app.domains.courses.service.dto.request.track_event_request_dto import TrackEventRequestDto
from app.domains.courses.service.dto.response.track_event_response_dto import TrackEventResponseDto


class TrackEventUseCase:

    def __init__(self, event_repository: EventRepository) -> None:
        self._repository = event_repository

    async def execute(self, dto: TrackEventRequestDto) -> TrackEventResponseDto:
        event_name = EventName(dto.event_name)

        event = Event(
            event_name=event_name.value,
            session_id=dto.session_id,
            created_at=datetime.utcnow(),
        )

        try:
            await self._repository.save(event)
            return TrackEventResponseDto(success=True)
        except Exception:
            return TrackEventResponseDto(success=False, message="이벤트 저장에 실패했습니다.")
