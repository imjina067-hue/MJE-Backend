from __future__ import annotations

from app.domains.courses.repository.orm.course_orm import CourseOrm
from app.domains.courses.repository.orm.course_place_orm import CoursePlaceOrm
from app.domains.recommendation.domain.entity.course_detail import (
    CourseDetail,
    PlaceDetail,
    SubCourse,
)


class CourseDetailMapper:
    @staticmethod
    def to_place_detail(orm: CoursePlaceOrm) -> PlaceDetail:
        return PlaceDetail(
            visit_order=orm.visit_order,
            name=orm.name,
            category=orm.category,
            duration_minutes=orm.duration_minutes,
            photo_url=orm.photo_url,
            description=orm.description,
            route_distance_m=orm.route_distance_m,
            route_duration_min=orm.route_duration_min,
            route_transport=orm.route_transport,
            route_polyline=orm.route_polyline,
        )

    @staticmethod
    def to_course_detail(course_orm: CourseOrm, place_orms: list[CoursePlaceOrm]) -> CourseDetail:
        return CourseDetail(
            course_id=course_orm.course_id,
            request_id=course_orm.request_id,
            title=course_orm.title,
            description=course_orm.description,
            total_duration=course_orm.total_duration,
            location_summary=course_orm.location_summary,
            route_summary=course_orm.route_summary,
            places=[CourseDetailMapper.to_place_detail(p) for p in place_orms],
        )

    @staticmethod
    def to_sub_course(orm: CourseOrm) -> SubCourse:
        return SubCourse(
            course_id=orm.course_id,
            course_type=orm.course_type,
            title=orm.title,
            route_summary=orm.route_summary,
            location_summary=orm.location_summary,
            total_duration=orm.total_duration,
        )
