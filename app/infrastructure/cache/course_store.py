from __future__ import annotations

from typing import Optional

from app.domains.recommendation.service.dto.response.create_course_response_dto import (
    CourseResultDto,
    CreateCourseResponseDto,
)


class CourseStore:
    def __init__(self) -> None:
        self._store: dict[str, CreateCourseResponseDto] = {}
        self._course_index: dict[str, str] = {}

    def save(self, course_id: str, dto: CreateCourseResponseDto) -> None:
        self._store[course_id] = dto
        for course in self._iter_courses(dto):
            self._course_index[course.course_id] = course_id

    def get(self, course_id: str) -> Optional[CreateCourseResponseDto]:
        if course_id in self._store:
            return self._store.get(course_id)

        recommendation_id = self._course_index.get(course_id)
        if recommendation_id is None:
            return None
        return self._store.get(recommendation_id)

    def get_course(self, course_id: str) -> Optional[CourseResultDto]:
        dto = self.get(course_id)
        if dto is None:
            return None
        if course_id in self._store:
            return dto.main_course
        return next((course for course in self._iter_courses(dto) if course.course_id == course_id), None)

    def get_other_courses(self, course_id: str) -> list[CourseResultDto]:
        dto = self.get(course_id)
        if dto is None:
            return []

        selected_course = self.get_course(course_id)
        if selected_course is None:
            return []

        return [
            course
            for course in self._iter_courses(dto)
            if course.course_id != selected_course.course_id
        ]

    def _iter_courses(self, dto: CreateCourseResponseDto) -> list[CourseResultDto]:
        courses: list[CourseResultDto] = []
        if dto.main_course is not None:
            courses.append(dto.main_course)
        courses.extend(dto.sub_courses)
        return courses
