from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.domains.recommendation.service.dto.response.create_course_response_dto import CreateCourseResponseDto


@runtime_checkable
class CourseStorePort(Protocol):
    def save(self, course_id: str, dto: CreateCourseResponseDto) -> None: ...
    def get(self, course_id: str) -> Optional[CreateCourseResponseDto]: ...
