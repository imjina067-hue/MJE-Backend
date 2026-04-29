from __future__ import annotations

from datetime import time
from typing import Optional

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place
from app.domains.recommendation.domain.value_object.time_slot import TimeSlot
from app.domains.recommendation.domain.value_object.transport import Transport

MEAL_ENTRY_POINTS: list[int] = [11 * 60 + 30, 17 * 60 + 30]  # 11:30, 17:30 in minutes

# 카테고리 전환 규칙 (RECOMMENDATION_SPEC.md §6)
CATEGORY_TRANSITIONS: dict[str, list[str]] = {
    "restaurant": ["cafe", "activity", "walk"],
    "cafe": ["activity", "walk", "restaurant"],
    "walk": ["cafe", "activity", "restaurant"],
    "activity": ["cafe", "restaurant", "walk"],
}


class CourseComposer:

    def compose(
        self,
        places_by_category: dict[str, list[Place]],
        time_slot: TimeSlot,
        transport: Transport,
        start_time: time,
    ) -> list[Course]:
        category_orders = self._get_category_orders(time_slot, start_time, places_by_category)
        courses: list[Course] = []

        for order in category_orders:
            candidates = self._generate_candidates(places_by_category, order, transport)
            courses.extend(candidates)

        return self._deduplicate_and_sort(courses)

    # ── 시작 카테고리 결정 (RECOMMENDATION_SPEC.md §6) ─────────────────────────

    def _determine_start_category(
        self,
        time_slot: TimeSlot,
        start_time: time,
        places_by_category: dict[str, list[Place]],
    ) -> str:
        if time_slot.is_late_night():
            return "restaurant" if places_by_category.get("restaurant") else "activity"

        minutes = start_time.hour * 60 + start_time.minute
        dist_to_nearest_meal = min(abs(minutes - ep) for ep in MEAL_ENTRY_POINTS)

        if dist_to_nearest_meal <= 60:
            return "restaurant"

        cafe_count = len(places_by_category.get("cafe", []))
        activity_count = len(places_by_category.get("activity", [])) + len(
            places_by_category.get("walk", [])
        )
        return "cafe" if cafe_count >= activity_count else "activity"

    # ── 카테고리 순서 생성 ────────────────────────────────────────────────────

    def _get_category_orders(
        self,
        time_slot: TimeSlot,
        start_time: time,
        places_by_category: dict[str, list[Place]],
    ) -> list[list[str]]:
        if time_slot.is_late_night():
            return [["restaurant", "activity"], ["activity", "restaurant"]]

        start = self._determine_start_category(time_slot, start_time, places_by_category)
        nexts = CATEGORY_TRANSITIONS[start]
        available = [c for c in nexts if places_by_category.get(c)]

        orders: list[list[str]] = []
        for second in available[:2]:
            thirds = [
                c for c in CATEGORY_TRANSITIONS[second]
                if c != start and c != second and places_by_category.get(c)
            ]
            for third in thirds[:1]:
                orders.append([start, second, third])

        return orders if orders else [[start] + available[:2]]

    # ── 코스 후보 생성 ────────────────────────────────────────────────────────

    def _generate_candidates(
        self,
        places_by_category: dict[str, list[Place]],
        category_order: list[str],
        transport: Transport,
    ) -> list[Course]:
        pools = [places_by_category.get(cat, [])[:5] for cat in category_order]
        if any(not pool for pool in pools):
            return []

        candidates: list[Course] = []
        for p0 in pools[0]:
            for p1 in (pools[1] if len(pools) > 1 else [None]):
                for p2 in (pools[2] if len(pools) > 2 else [None]):
                    place_list = [x for x in [p0, p1, p2] if x is not None]
                    if len({p.name for p in place_list}) != len(place_list):
                        continue
                    course = self._build_course(place_list, transport)
                    if course is not None:
                        candidates.append(course)
        return candidates

    def _build_course(
        self,
        places: list[Place],
        transport: Transport,
    ) -> Optional[Course]:
        course = Course(course_type="", transport=transport.value)
        total_candidate_count = len(places)

        for i, place in enumerate(places):
            travel_time: Optional[int] = None
            if i < len(places) - 1:
                dist = place.distance_to_meters(places[i + 1])
                travel_minutes = int((dist / transport.speed_mps()) / 60)
                if travel_minutes > transport.max_travel_minutes():
                    return None  # 이동수단 제약 초과 → 해당 조합 제외
                travel_time = travel_minutes
            course.add_place(place, order=i + 1, travel_time=travel_time)

        course.total_score = sum(
            p.calculate_total_score(total_candidate_count) for p in places
        )
        return course

    # ── 중복 제거 및 정렬 ─────────────────────────────────────────────────────

    def _deduplicate_and_sort(self, courses: list[Course]) -> list[Course]:
        seen: set[frozenset[str]] = set()
        unique: list[Course] = []
        for course in sorted(courses, key=lambda c: c.total_score, reverse=True):
            key = course.place_name_set()
            if key not in seen:
                seen.add(key)
                unique.append(course)
        return unique
