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

PRIMARY_POOL_LIMIT = 8
FALLBACK_POOL_LIMIT = 12
TIER_SIZE = 4


class CourseComposer:

    def compose(
        self,
        places_by_category: dict[str, list[Place]],
        time_slot: TimeSlot,
        transport: Transport,
        start_time: time,
    ) -> list[Course]:
        primary_orders = self._get_category_orders(
            time_slot,
            start_time,
            places_by_category,
            expanded=False,
        )
        primary_courses = self._collect_candidates(
            places_by_category,
            primary_orders,
            transport,
            pool_limit=PRIMARY_POOL_LIMIT,
        )
        unique_primary = self._deduplicate_and_sort(primary_courses)
        if len(unique_primary) >= 3:
            return unique_primary

        fallback_orders = self._get_category_orders(
            time_slot,
            start_time,
            places_by_category,
            expanded=True,
        )
        fallback_courses = self._collect_candidates(
            places_by_category,
            fallback_orders,
            transport,
            pool_limit=FALLBACK_POOL_LIMIT,
        )
        return self._deduplicate_and_sort(primary_courses + fallback_courses)

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
        expanded: bool = False,
    ) -> list[list[str]]:
        if time_slot.is_late_night():
            base_orders = [["restaurant", "activity"], ["activity", "restaurant"]]
            return base_orders if not expanded else self._unique_orders(base_orders)

        start = self._determine_start_category(time_slot, start_time, places_by_category)
        starts = [start]
        alt_starts = [
            c for c in CATEGORY_TRANSITIONS
            if c != start and places_by_category.get(c)
        ]
        if expanded:
            starts.extend(alt_starts)
        else:
            starts.extend(alt_starts[:2])

        orders: list[list[str]] = []
        for current_start in starts:
            nexts = CATEGORY_TRANSITIONS[current_start]
            available = [c for c in nexts if places_by_category.get(c)]
            second_candidates = available if expanded else available[:3]

            current_orders: list[list[str]] = []
            for second in second_candidates:
                thirds = [
                    c for c in CATEGORY_TRANSITIONS[second]
                    if c != current_start and c != second and places_by_category.get(c)
                ]
                third_candidates = thirds if expanded else thirds[:2]
                for third in third_candidates:
                    current_orders.append([current_start, second, third])

            if current_orders:
                orders.extend(current_orders)
            else:
                fallback_order = [current_start] + (available[:2] if not expanded else available)
                if len(fallback_order) >= 2:
                    orders.append(fallback_order)

        return self._unique_orders(orders)

    def _collect_candidates(
        self,
        places_by_category: dict[str, list[Place]],
        category_orders: list[list[str]],
        transport: Transport,
        pool_limit: int,
    ) -> list[Course]:
        courses: list[Course] = []
        for order in category_orders:
            candidates = self._generate_candidates(
                places_by_category,
                order,
                transport,
                pool_limit=pool_limit,
            )
            courses.extend(candidates)
        return courses

    # ── 코스 후보 생성 ────────────────────────────────────────────────────────

    def _generate_candidates(
        self,
        places_by_category: dict[str, list[Place]],
        category_order: list[str],
        transport: Transport,
        pool_limit: int = PRIMARY_POOL_LIMIT,
    ) -> list[Course]:
        full_pools = [places_by_category.get(cat, [])[:pool_limit] for cat in category_order]
        if any(not pool for pool in full_pools):
            return []

        tier = min(TIER_SIZE, pool_limit)
        primary = [p[:tier] for p in full_pools]

        pool_variants: list[list[list[Place]]] = [primary]
        for i, pool in enumerate(full_pools):
            secondary = pool[tier:]
            if secondary:
                variant = [secondary if j == i else primary[j] for j in range(len(full_pools))]
                pool_variants.append(variant)

        candidates: list[Course] = []
        for pools in pool_variants:
            candidates.extend(self._cartesian_build(pools, transport))
        return candidates

    def _cartesian_build(self, pools: list[list[Place]], transport: Transport) -> list[Course]:
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
        unique: list[Course] = []
        for course in sorted(courses, key=lambda c: c.total_score, reverse=True):
            if not any(self._is_near_duplicate(accepted, course) for accepted in unique):
                unique.append(course)
        return unique

    def _is_near_duplicate(self, a: Course, b: Course) -> bool:
        return (
            len(a.place_name_set() & b.place_name_set()) >= 2
            or a.first_place_name() == b.first_place_name()
        )

    def _unique_orders(self, orders: list[list[str]]) -> list[list[str]]:
        seen: set[tuple[str, ...]] = set()
        unique: list[list[str]] = []
        for order in orders:
            key = tuple(order)
            if key in seen:
                continue
            seen.add(key)
            unique.append(order)
        return unique
