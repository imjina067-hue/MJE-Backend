from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, field_validator

from app.domains.recommendation.service.dto.request.create_course_request_dto import CreateCourseRequestDto

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class CreateCourseRequestForm(BaseModel):
    area: str
    start_time: str
    transport: Literal["car", "walk", "public_transit"]

    @field_validator("area")
    @classmethod
    def validate_area(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("장소를 입력해주세요.")
        return v

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError("시간은 HH:MM 형식으로 입력해주세요.")
        h, m = map(int, v.split(":"))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("유효하지 않은 시간입니다.")
        total = h * 60 + m
        # 서비스 가능 시간: 09:00 ~ 01:00
        in_service = (total >= 9 * 60) or (total < 60)
        if not in_service:
            raise ValueError("서비스 가능 시간은 09:00 ~ 01:00입니다.")
        return v

    def to_request(self) -> CreateCourseRequestDto:
        return CreateCourseRequestDto(
            area=self.area,
            start_time=self.start_time,
            transport=self.transport,
        )
