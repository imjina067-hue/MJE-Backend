from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExplainTextDto:
    name: str
    description: str


@dataclass
class HashtagDto:
    keywords: list[str]


@dataclass
class LocationDto:
    location: str


@dataclass
class CourseImageDto:
    image_url: Optional[str]


@dataclass
class PlaceItemDto:
    id: str
    name: str
    description: str
    location: str
    time: Optional[str]
    image_url: Optional[str]


@dataclass
class RestaurantsDto:
    restaurants: list[PlaceItemDto] = field(default_factory=list)


@dataclass
class CafesDto:
    cafes: list[PlaceItemDto] = field(default_factory=list)


@dataclass
class ActivitiesDto:
    activities: list[PlaceItemDto] = field(default_factory=list)


@dataclass
class OtherCourseItemDto:
    id: str
    course_id: str
    name: str
    description: str
    locations: list[str]
    duration: Optional[int]
    image_url: Optional[str]


@dataclass
class OtherCoursesDto:
    courses: list[OtherCourseItemDto] = field(default_factory=list)
