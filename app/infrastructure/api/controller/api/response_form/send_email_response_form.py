from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.infrastructure.api.service.dto.response.send_email_response_dto import SendEmailResponseDto


class SendEmailResponseForm(BaseModel):
    success: bool
    message: Optional[str] = None

    @classmethod
    def from_response(cls, dto: SendEmailResponseDto) -> SendEmailResponseForm:
        return cls(success=dto.success, message=dto.message)
