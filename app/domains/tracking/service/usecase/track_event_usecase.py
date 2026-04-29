from __future__ import annotations

from datetime import datetime

from app.domains.tracking.domain.entity.event import Event
from app.domains.tracking.domain.exception import InvalidEventNameException
from app.domains.tracking.domain.value_object.event_name import EventName
from app.domains.tracking.repository.event_repository import EventRepository
from app.domains.tracking.service.dto.request.track_event_request_dto import TrackEventRequestDto
from app.domains.tracking.service.dto.response.track_event_response_dto import TrackEventResponseDto


class TrackEventUseCase:

    def __init__(self, event_repository: EventRepository) -> None:
        self._repository = event_repository

    async def execute(self, dto: TrackEventRequestDto) -> TrackEventResponseDto:
        event_name = EventName(dto.event_name)  # 도메인 검증 — 실패 시 400

        event = Event(
            event_name=event_name.value,
            session_id=dto.session_id,
            created_at=datetime.utcnow(),
        )

        try:
            await self._repository.save(event)
            return TrackEventResponseDto(success=True)
        except Exception:
            # 저장 실패 시 서버 종료 없이 실패 응답 반환
            return TrackEventResponseDto(success=False, message="이벤트 저장에 실패했습니다.")
