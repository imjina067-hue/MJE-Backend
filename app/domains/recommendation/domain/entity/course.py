from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.domains.recommendation.domain.entity.place import Place

CATEGORY_DURATION_MINUTES: dict[str, int] = {
    "restaurant": 90,
    "cafe": 60,
    "walk": 90,
    "activity": 120,
}


@dataclass
class CoursePlace:
    place: Place
    visit_order: int
    estimated_duration_minutes: int
    travel_time_to_next_minutes: Optional[int] = None


@dataclass
class Course:
    course_type: str        # "main" | "sub1" | "sub2"
    transport: str
    total_score: float = 0.0
    places: list[CoursePlace] = field(default_factory=list)

    def add_place(self, place: Place, order: int, travel_time: Optional[int] = None) -> None:
        duration = CATEGORY_DURATION_MINUTES.get(place.category, 60)
        self.places.append(
            CoursePlace(
                place=place,
                visit_order=order,
                estimated_duration_minutes=duration,
                travel_time_to_next_minutes=travel_time,
            )
        )

    def total_duration_minutes(self) -> int:
        stay = sum(cp.estimated_duration_minutes for cp in self.places)
        travel = sum(cp.travel_time_to_next_minutes or 0 for cp in self.places[:-1])
        return stay + travel

    def has_duplicate_category(self) -> bool:
        cats = [cp.place.category for cp in self.places]
        return len(cats) != len(set(cats))

    def has_duplicate_place(self) -> bool:
        names = [cp.place.name for cp in self.places]
        return len(names) != len(set(names))

    def place_name_set(self) -> frozenset[str]:
        return frozenset(cp.place.name for cp in self.places)

    def all_keywords(self) -> set[str]:
        result: set[str] = set()
        for cp in self.places:
            result.update(cp.place.keywords)
        return result
