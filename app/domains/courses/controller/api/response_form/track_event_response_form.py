from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domains.courses.service.dto.response.track_event_response_dto import TrackEventResponseDto


class TrackEventResponseForm(BaseModel):
    success: bool
    message: Optional[str] = None

    @classmethod
    def from_response(cls, dto: TrackEventResponseDto) -> TrackEventResponseForm:
        return cls(success=dto.success, message=dto.message)
