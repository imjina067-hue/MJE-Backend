from __future__ import annotations


class CourseNotFoundException(Exception):
    def __init__(self, course_id: str) -> None:
        super().__init__(f"코스를 찾을 수 없습니다: {course_id}")
