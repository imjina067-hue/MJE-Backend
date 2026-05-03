from __future__ import annotations

import json

from app.domains.recommendation.domain.exception import CourseNotFoundException
from app.domains.recommendation.service.dto.response.create_course_response_dto import CourseResultDto
from app.domains.recommendation.service.dto.response.get_course_detail_response_dto import (
    GetCourseDetailResponseDto,
    PlaceDetailDto,
    SubCourseDto,
)
from app.domains.recommendation.service.port.course_store_port import CourseStorePort


class GetCourseDetailUseCase:
    def __init__(self, course_store: CourseStorePort) -> None:
        self._store = course_store

    async def execute(self, course_id: str) -> GetCourseDetailResponseDto:
        course = self._store.get_course(course_id)
        if course is None:
            raise CourseNotFoundException(course_id)

        sub_courses = self._store.get_other_courses(course_id)

        return GetCourseDetailResponseDto(
            course_id=course.course_id,
            title=self._build_title(course),
            description=self._build_description(course),
            total_duration=course.total_duration_minutes,
            location_summary=self._build_location_summary(course),
            route_summary=self._build_route_summary(course),
            places=[
                PlaceDetailDto(
                    visit_order=place.visit_order,
                    name=place.name,
                    category=place.category,
                    duration_minutes=place.estimated_duration_minutes,
                    photo_url=place.image_url,
                    description=place.main_description,
                    route_distance_m=None,
                    route_duration_min=place.travel_time_to_next_minutes,
                    route_transport=course.transport if place.travel_time_to_next_minutes is not None else None,
                    route_polyline=json.dumps(place.route_path_to_next) if place.route_path_to_next else None,
                )
                for place in course.places
            ],
            sub_courses=[
                SubCourseDto(
                    course_id=other.course_id,
                    course_type=other.course_type,
                    title=self._build_title(other),
                    route_summary=self._build_route_summary(other),
                    location_summary=self._build_location_summary(other),
                    total_duration=other.total_duration_minutes,
                )
                for other in sub_courses
            ],
        )

    def _build_title(self, course: CourseResultDto) -> str:
        area = course.places[0].area if course.places else ""
        return f"{area} {course.course_type}".strip()

    def _build_description(self, course: CourseResultDto) -> str:
        names = ", ".join(place.name for place in course.places[:3])
        return names if names else course.course_type

    def _build_location_summary(self, course: CourseResultDto) -> str:
        areas = list(dict.fromkeys(place.area for place in course.places if place.area))
        return ", ".join(areas)

    def _build_route_summary(self, course: CourseResultDto) -> str:
        return " -> ".join(place.name for place in course.places)
