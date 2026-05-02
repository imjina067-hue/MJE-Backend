from __future__ import annotations

from typing import Optional

from app.domains.recommendation.service.dto.response.create_course_response_dto import CreateCourseResponseDto


class CourseStore:
    def __init__(self) -> None:
        self._store: dict[str, CreateCourseResponseDto] = {}

    def save(self, course_id: str, dto: CreateCourseResponseDto) -> None:
        self._store[course_id] = dto

    def get(self, course_id: str) -> Optional[CreateCourseResponseDto]:
        return self._store.get(course_id)
