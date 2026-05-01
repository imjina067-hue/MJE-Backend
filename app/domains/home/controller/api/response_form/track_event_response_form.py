from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer

from app.domains.home.service.dto.response.track_event_response_dto import TrackEventResponseDto


class TrackEventResponseForm(BaseModel):
    event_name: str
    session_id: str
    timestamp: datetime
    page_path: str

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        if value.tzinfo is None:
            utc_dt = value.replace(tzinfo=timezone.utc)
        else:
            utc_dt = value.astimezone(timezone.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc_dt.microsecond // 1000:03d}Z"

    @classmethod
    def from_response(cls, dto: TrackEventResponseDto) -> TrackEventResponseForm:
        return cls(
            event_name=dto.event_name,
            session_id=dto.session_id,
            timestamp=dto.timestamp,
            page_path=dto.page_path,
        )
