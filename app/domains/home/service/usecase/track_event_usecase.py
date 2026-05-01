from __future__ import annotations

from app.domains.home.domain.entity.event import Event
from app.domains.home.domain.value_object.event_name import EventName
from app.domains.home.repository.event_repository import EventRepository
from app.domains.home.service.dto.request.track_event_request_dto import TrackEventRequestDto
from app.domains.home.service.dto.response.track_event_response_dto import TrackEventResponseDto


class TrackEventUseCase:

    def __init__(self, event_repository: EventRepository) -> None:
        self._repository = event_repository

    async def execute(self, dto: TrackEventRequestDto) -> TrackEventResponseDto:
        event_name = EventName(dto.event_name)

        event = Event(
            event_name=event_name.value,
            session_id=dto.session_id,
            page_path=dto.page_path,
            created_at=dto.timestamp,
        )

        await self._repository.save(event)

        return TrackEventResponseDto(
            event_name=event.event_name,
            session_id=event.session_id,
            timestamp=event.created_at,
            page_path=event.page_path,
        )
