from __future__ import annotations

from app.domains.recommendation.domain.exception import CourseNotFoundException
from app.domains.recommendation.repository.course_detail_repository import CourseDetailRepository
from app.domains.recommendation.service.dto.response.get_course_detail_response_dto import (
    GetCourseDetailResponseDto,
    PlaceDetailDto,
    SubCourseDto,
)


class GetCourseDetailUseCase:
    def __init__(self, course_detail_repository: CourseDetailRepository) -> None:
        self._repository = course_detail_repository

    async def execute(self, course_id: str) -> GetCourseDetailResponseDto:
        detail = await self._repository.find_by_course_id(course_id)
        if detail is None:
            raise CourseNotFoundException(course_id)

        sub_courses = await self._repository.find_others_by_request_id(
            detail.request_id, course_id
        )

        return GetCourseDetailResponseDto(
            course_id=detail.course_id,
            title=detail.title,
            description=detail.description,
            total_duration=detail.total_duration,
            location_summary=detail.location_summary,
            route_summary=detail.route_summary,
            places=[
                PlaceDetailDto(
                    visit_order=p.visit_order,
                    name=p.name,
                    category=p.category,
                    duration_minutes=p.duration_minutes,
                    photo_url=p.photo_url,
                    description=p.description,
                    route_distance_m=p.route_distance_m,
                    route_duration_min=p.route_duration_min,
                    route_transport=p.route_transport,
                    route_polyline=p.route_polyline,
                )
                for p in detail.places
            ],
            sub_courses=[
                SubCourseDto(
                    course_id=s.course_id,
                    course_type=s.course_type,
                    title=s.title,
                    route_summary=s.route_summary,
                    location_summary=s.location_summary,
                    total_duration=s.total_duration,
                )
                for s in sub_courses
            ],
        )
