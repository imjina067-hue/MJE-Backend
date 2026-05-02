from __future__ import annotations

from pydantic import BaseModel, field_validator

from app.infrastructure.api.service.dto.request.track_export_event_request_dto import TrackExportEventRequestDto


class TrackExportEventRequestForm(BaseModel):
    event_name: str
    session_id: str
    page_path: str

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("이벤트명을 입력해주세요.")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("session_id를 입력해주세요.")
        return v.strip()

    @field_validator("page_path")
    @classmethod
    def validate_page_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("page_path를 입력해주세요.")
        return v.strip()

    def to_request(self) -> TrackExportEventRequestDto:
        return TrackExportEventRequestDto(
            event_name=self.event_name,
            session_id=self.session_id,
            page_path=self.page_path,
        )
