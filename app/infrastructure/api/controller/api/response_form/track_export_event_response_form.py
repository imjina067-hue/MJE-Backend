from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.infrastructure.api.service.dto.response.track_export_event_response_dto import TrackExportEventResponseDto


class TrackExportEventResponseForm(BaseModel):
    success: bool
    message: Optional[str] = None

    @classmethod
    def from_response(cls, dto: TrackExportEventResponseDto) -> TrackExportEventResponseForm:
        return cls(success=dto.success, message=dto.message)
