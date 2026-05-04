from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domains.recommendation.service.dto.response.create_course_response_dto import (
    CourseTitlePlaceDto,
    CourseResultDto,
    CreateCourseResponseDto,
    PlaceResultDto,
)


class PlaceResponseItem(BaseModel):
    visitOrder: int
    name: str
    area: str
    category: str
    imageUrl: Optional[str]
    mainDescription: str
    briefDescription: str
    keywords: list[str]
    estimatedDurationMinutes: int
    travelTimeToNextMinutes: Optional[int]
    recommendedTimeSlot: str
    hasParking: Optional[bool]
    routePathToNext: list[list[float]] = []  # [[lat, lng], ...]


class CourseTitlePlaceResponseItem(BaseModel):
    name: str
    category: str
    subCategory: str


class CourseResponseItem(BaseModel):
    courseId: str
    courseType: str
    region: str
    mainPlace: Optional[CourseTitlePlaceResponseItem]
    subPlaces: list[CourseTitlePlaceResponseItem]
    title: str
    description: str
    transport: str
    totalDurationMinutes: int
    imageUrl: Optional[str]
    places: list[PlaceResponseItem]


class CreateCourseResponseForm(BaseModel):
    recommendationId: str
    courseId: str
    mainCourse: Optional[CourseResponseItem]
    subCourses: list[CourseResponseItem]
    message: Optional[str] = None

    @classmethod
    def from_response(cls, dto: CreateCourseResponseDto) -> CreateCourseResponseForm:
        return cls(
            recommendationId=dto.course_id,
            courseId=dto.course_id,
            mainCourse=cls._map_course(dto.main_course) if dto.main_course else None,
            subCourses=[cls._map_course(c) for c in dto.sub_courses],
            message=dto.message,
        )

    @classmethod
    def _map_course(cls, course: CourseResultDto) -> CourseResponseItem:
        return CourseResponseItem(
            courseId=course.course_id,
            courseType=course.course_type,
            region=course.region,
            mainPlace=cls._map_title_place(course.main_place),
            subPlaces=[cls._map_title_place(place) for place in course.sub_places],
            title=course.title,
            description=course.description,
            transport=course.transport,
            totalDurationMinutes=course.total_duration_minutes,
            imageUrl=course.image_url,
            places=[cls._map_place(p) for p in course.places],
        )

    @classmethod
    def _map_title_place(cls, place: CourseTitlePlaceDto | None) -> Optional[CourseTitlePlaceResponseItem]:
        if place is None:
            return None
        return CourseTitlePlaceResponseItem(
            name=place.name,
            category=place.category,
            subCategory=place.sub_category,
        )

    @classmethod
    def _map_place(cls, place: PlaceResultDto) -> PlaceResponseItem:
        return PlaceResponseItem(
            visitOrder=place.visit_order,
            name=place.name,
            area=place.area,
            category=place.category,
            imageUrl=place.image_url,
            mainDescription=place.main_description,
            briefDescription=place.brief_description,
            keywords=place.keywords,
            estimatedDurationMinutes=place.estimated_duration_minutes,
            travelTimeToNextMinutes=place.travel_time_to_next_minutes,
            recommendedTimeSlot=place.recommended_time_slot,
            hasParking=place.has_parking,
            routePathToNext=[[lat, lng] for lat, lng in place.route_path_to_next],
        )
