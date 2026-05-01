from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.domains.recommendation.domain.entity.course_detail import CourseDetail, SubCourse


@runtime_checkable
class CourseDetailRepository(Protocol):
    async def find_by_course_id(self, course_id: str) -> Optional[CourseDetail]: ...

    async def find_others_by_request_id(
        self, request_id: str, exclude_course_id: str
    ) -> list[SubCourse]: ...
