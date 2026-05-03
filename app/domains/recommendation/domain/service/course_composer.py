from __future__ import annotations

import random
from typing import Optional

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place
from app.domains.recommendation.domain.service.recommendation_config import (
    COURSE_PATTERNS,
    FALLBACK_COURSE_PATTERNS,
    TOP_N_CANDIDATES,
)
from app.domains.recommendation.domain.value_object.time_slot import TimeSlot
from app.domains.recommendation.domain.value_object.transport import Transport


class CourseComposer:
    _MAX_PATTERN_ATTEMPTS = 8
    _MAX_PLACE_ATTEMPTS_PER_PATTERN = 4

    def compose(
        self,
        places_by_category: dict[str, list[Place]],
        time_slot: TimeSlot,
        transport: Transport,
        seed: Optional[int] = None,
    ) -> list[Course]:
        rng = random.Random(seed)

        # 카테고리별 score 내림차순 상위 N개 추출
        top: dict[str, list[Place]] = {
            cat: sorted(places, key=lambda p: p.score, reverse=True)[:TOP_N_CANDIDATES]
            for cat, places in places_by_category.items()
            if places
        }

        preferred_starts = self._preferred_starts(time_slot)
        used_names: set[str] = set()
        used_patterns: set[tuple] = set()
        courses: list[Course] = []
        full_patterns = self._available_patterns(top, COURSE_PATTERNS)
        fallback_patterns = self._available_patterns(top, FALLBACK_COURSE_PATTERNS)

        for course_type in ("main", "sub1", "sub2"):
            pattern_pool = full_patterns if full_patterns else fallback_patterns
            if not pattern_pool:
                break

            course = None
            selected_pattern = None
            attempt_plans = self._attempt_plans(
                course_type=course_type,
                pattern_pool=pattern_pool,
                fallback_patterns=fallback_patterns,
            )
            for patterns, avoid_used_patterns, avoid_used_names in attempt_plans:
                for pattern in self._pattern_attempt_order(
                    patterns,
                    preferred_starts,
                    used_patterns,
                    rng,
                    avoid_used_patterns=avoid_used_patterns,
                ):
                    course = self._build_course_with_retries(
                        top,
                        pattern,
                        transport,
                        used_names,
                        course_type,
                        rng,
                        avoid_used_names=avoid_used_names,
                    )
                    if course is not None:
                        selected_pattern = pattern
                        break
                if course is not None:
                    break
            if course is not None:
                courses.append(course)
                used_names.update(course.place_name_set())
                if selected_pattern is not None:
                    used_patterns.add(tuple(selected_pattern))

        return courses

    def _preferred_starts(self, time_slot: TimeSlot) -> list[str]:
        slot = time_slot.value
        if slot == "late_night":
            return ["restaurant", "activity"]
        if slot in ("lunch", "evening"):
            return ["restaurant", "activity", "cafe"]
        return ["cafe", "walk", "activity"]

    def _pick_pattern(
        self,
        available: list[list[str]],
        preferred_starts: list[str],
        used_patterns: set[tuple],
        rng: random.Random,
        avoid_used_patterns: bool = True,
    ) -> list[str]:
        if avoid_used_patterns:
            unused = [p for p in available if tuple(p) not in used_patterns]
            pool = unused if unused else available
        else:
            pool = available
        preferred = [p for p in pool if p[0] in preferred_starts]
        return rng.choice(preferred if preferred else pool)

    def _pattern_attempt_order(
        self,
        available: list[list[str]],
        preferred_starts: list[str],
        used_patterns: set[tuple],
        rng: random.Random,
        avoid_used_patterns: bool,
    ) -> list[list[str]]:
        if avoid_used_patterns:
            unused = [pattern for pattern in available if tuple(pattern) not in used_patterns]
            pool = unused if unused else available
        else:
            pool = available

        preferred = [pattern for pattern in pool if pattern[0] in preferred_starts]
        others = [pattern for pattern in pool if pattern[0] not in preferred_starts]
        rng.shuffle(preferred)
        rng.shuffle(others)
        ordered = preferred + others
        return ordered[: self._MAX_PATTERN_ATTEMPTS]

    def _available_patterns(
        self,
        top: dict[str, list[Place]],
        patterns: list[list[str]],
    ) -> list[list[str]]:
        return [pattern for pattern in patterns if all(top.get(cat) for cat in pattern)]

    def _build_course(
        self,
        top: dict[str, list[Place]],
        pattern: list[str],
        transport: Transport,
        used_names: set[str],
        course_type: str,
        rng: random.Random,
        avoid_used_names: bool = True,
    ) -> Optional[Course]:
        course = Course(course_type=course_type, transport=transport.value)
        selected: list[Place] = []
        course_used: set[str] = set()

        for cat in pattern:
            pool = top.get(cat, [])
            if avoid_used_names:
                fresh = [p for p in pool if p.name not in used_names and p.name not in course_used]
                candidates = fresh or [p for p in pool if p.name not in course_used]
            else:
                candidates = [p for p in pool if p.name not in course_used]
            if not candidates:
                return None

            weights = [max(p.score, 0.01) for p in candidates]
            place = rng.choices(candidates, weights=weights, k=1)[0]
            selected.append(place)
            course_used.add(place.name)

        for i, place in enumerate(selected):
            travel_time: Optional[int] = None
            if i < len(selected) - 1:
                dist = place.distance_to_meters(selected[i + 1])
                minutes = int(dist / transport.speed_mps() / 60)
                if minutes > transport.max_travel_minutes():
                    return None
                travel_time = minutes
            course.add_place(place, order=i + 1, travel_time=travel_time)

        course.total_score = sum(p.score for p in selected)
        return course

    def _build_course_with_retries(
        self,
        top: dict[str, list[Place]],
        pattern: list[str],
        transport: Transport,
        used_names: set[str],
        course_type: str,
        rng: random.Random,
        avoid_used_names: bool,
    ) -> Optional[Course]:
        for _ in range(self._MAX_PLACE_ATTEMPTS_PER_PATTERN):
            course = self._build_course(
                top,
                pattern,
                transport,
                used_names,
                course_type,
                rng,
                avoid_used_names=avoid_used_names,
            )
            if course is not None:
                return course
        return None

    def _attempt_plans(
        self,
        course_type: str,
        pattern_pool: list[list[str]],
        fallback_patterns: list[list[str]],
    ) -> list[tuple[list[list[str]], bool, bool]]:
        plans: list[tuple[list[list[str]], bool, bool]] = [
            (pattern_pool, True, True),
        ]
        if fallback_patterns and fallback_patterns is not pattern_pool:
            plans.append((fallback_patterns, True, True))
        if course_type != "main":
            plans.append((pattern_pool, False, True))
            if fallback_patterns and fallback_patterns is not pattern_pool:
                plans.append((fallback_patterns, False, True))
            plans.append((pattern_pool, False, False))
            if fallback_patterns and fallback_patterns is not pattern_pool:
                plans.append((fallback_patterns, False, False))
        return plans
