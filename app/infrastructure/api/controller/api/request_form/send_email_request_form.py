from __future__ import annotations

from pydantic import BaseModel, EmailStr, field_validator

from app.infrastructure.api.service.dto.request.send_email_request_dto import SendEmailRequestDto


class SendEmailRequestForm(BaseModel):
    email: EmailStr
    course_id: str

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("course_id를 입력해주세요.")
        return v.strip()

    def to_request(self) -> SendEmailRequestDto:
        return SendEmailRequestDto(
            email=str(self.email),
            course_id=self.course_id,
        )
