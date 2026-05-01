from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlaceDetailDto:
    visit_order: int
    name: str
    category: str
    duration_minutes: int
    photo_url: Optional[str]
    description: Optional[str]
    route_distance_m: Optional[int]
    route_duration_min: Optional[int]
    route_transport: Optional[str]
    route_polyline: Optional[str]


@dataclass
class SubCourseDto:
    course_id: str
    course_type: str
    title: str
    route_summary: str
    location_summary: str
    total_duration: int


@dataclass
class GetCourseDetailResponseDto:
    course_id: str
    title: str
    description: str
    total_duration: int
    location_summary: str
    route_summary: str
    places: list[PlaceDetailDto] = field(default_factory=list)
    sub_courses: list[SubCourseDto] = field(default_factory=list)
