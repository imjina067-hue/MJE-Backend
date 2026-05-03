from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlaceResultDto:
    visit_order: int
    name: str
    area: str
    category: str
    main_description: str
    brief_description: str
    keywords: list[str]
    estimated_duration_minutes: int
    recommended_time_slot: str
    image_url: Optional[str] = None
    travel_time_to_next_minutes: Optional[int] = None
    has_parking: Optional[bool] = None
    route_path_to_next: list[tuple[float, float]] = field(default_factory=list)


@dataclass
class CourseResultDto:
    course_id: str
    course_type: str          # "main" | "sub1" | "sub2"
    transport: str
    total_duration_minutes: int
    image_url: Optional[str] = None
    places: list[PlaceResultDto] = field(default_factory=list)


@dataclass
class CreateCourseResponseDto:
    course_id: str
    main_course: Optional[CourseResultDto]
    sub_courses: list[CourseResultDto]
    message: Optional[str] = None
