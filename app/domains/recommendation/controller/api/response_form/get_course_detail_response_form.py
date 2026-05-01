from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domains.recommendation.service.dto.response.get_course_detail_response_dto import (
    GetCourseDetailResponseDto,
    PlaceDetailDto,
    SubCourseDto,
)


class PlaceDetailItem(BaseModel):
    visitOrder: int
    name: str
    category: str
    durationMinutes: int
    photoUrl: Optional[str]
    description: Optional[str]
    routeDistanceM: Optional[int]
    routeDurationMin: Optional[int]
    routeTransport: Optional[str]
    routePolyline: Optional[str]


class SubCourseItem(BaseModel):
    courseId: str
    courseType: str
    title: str
    routeSummary: str
    locationSummary: str
    totalDuration: int


class GetCourseDetailResponseForm(BaseModel):
    courseId: str
    title: str
    description: str
    totalDuration: int
    locationSummary: str
    routeSummary: str
    places: list[PlaceDetailItem]
    subCourses: list[SubCourseItem]

    @classmethod
    def from_response(cls, dto: GetCourseDetailResponseDto) -> GetCourseDetailResponseForm:
        return cls(
            courseId=dto.course_id,
            title=dto.title,
            description=dto.description,
            totalDuration=dto.total_duration,
            locationSummary=dto.location_summary,
            routeSummary=dto.route_summary,
            places=[cls._map_place(p) for p in dto.places],
            subCourses=[cls._map_sub_course(s) for s in dto.sub_courses],
        )

    @classmethod
    def _map_place(cls, dto: PlaceDetailDto) -> PlaceDetailItem:
        return PlaceDetailItem(
            visitOrder=dto.visit_order,
            name=dto.name,
            category=dto.category,
            durationMinutes=dto.duration_minutes,
            photoUrl=dto.photo_url,
            description=dto.description,
            routeDistanceM=dto.route_distance_m,
            routeDurationMin=dto.route_duration_min,
            routeTransport=dto.route_transport,
            routePolyline=dto.route_polyline,
        )

    @classmethod
    def _map_sub_course(cls, dto: SubCourseDto) -> SubCourseItem:
        return SubCourseItem(
            courseId=dto.course_id,
            courseType=dto.course_type,
            title=dto.title,
            routeSummary=dto.route_summary,
            locationSummary=dto.location_summary,
            totalDuration=dto.total_duration,
        )
