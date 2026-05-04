from __future__ import annotations

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place
from app.domains.recommendation.domain.service.recommendation_config import (
    FRANCHISE_SCORE_MULTIPLIER,
    NIGHTLIFE_SIGNALS,
    PARKING_BONUS,
    SCORE_WEIGHTS,
)
from app.domains.recommendation.domain.value_object.time_slot import TimeSlot
from app.domains.recommendation.domain.value_object.transport import Transport


class RuleScorer:
    _TIME_SLOT_ACTIVITY_BONUS: dict[str, dict[str, float]] = {
        "morning": {
            "walk": 0.45,
            "culture": 0.35,
        },
        "lunch": {
            "culture": 0.4,
            "experience": 0.3,
            "walk": 0.25,
            "shopping": 0.25,
        },
        "afternoon": {
            "culture": 0.45,
            "experience": 0.4,
            "walk": 0.35,
            "shopping": 0.3,
        },
        "evening": {
            "nightlife": 0.5,
            "walk": 0.35,
            "culture": 0.25,
            "experience": 0.2,
        },
        "late_night": {
            "nightlife": 0.55,
            "walk": 0.25,
            "culture": 0.15,
        },
    }

    def apply_scores(
        self,
        places_by_category: dict[str, list[Place]],
        category_trends: dict[str, float],
        time_slot: TimeSlot,
        transport: Transport,
    ) -> None:
        """각 Place의 score 필드를 in-place로 설정한다."""
        for category, places in places_by_category.items():
            total = len(places)
            trend = category_trends.get(category, 0.0)
            for place in places:
                place.score = self._compute_score(place, total, trend, time_slot, transport)

    def _compute_score(
        self,
        place: Place,
        total: int,
        trend: float,
        time_slot: TimeSlot,
        transport: Transport,
    ) -> float:
        # 낮 시간대 야간 업소 → 사실상 제외 (가중 랜덤에서 거의 안 뽑힘)
        if self._is_time_inappropriate(place, time_slot):
            return 0.001

        rank_score = (total - place.search_rank + 1) / total if total > 0 and place.search_rank > 0 else 0.0
        rating_score = place.rating / 5.0
        time_fit = self._time_fit(place, time_slot)

        score = (
            rank_score     * SCORE_WEIGHTS["search_rank"]
            + rating_score * SCORE_WEIGHTS["rating"]
            + trend        * SCORE_WEIGHTS["trend"]
            + time_fit     * SCORE_WEIGHTS["time_fit"]
        )
        if transport.requires_parking_check() and place.has_parking:
            score += PARKING_BONUS
        if place.is_franchise:
            score *= FRANCHISE_SCORE_MULTIPLIER
        return score

    def _time_fit(self, place: Place, time_slot: TimeSlot) -> float:
        """시간대에 맞는 activity subtype과 야간 업소에 가산점."""
        score = 1.0

        if place.category == "activity" and place.activity_subtype:
            bonus = self._TIME_SLOT_ACTIVITY_BONUS.get(time_slot.value, {}).get(place.activity_subtype, 0.0)
            score += bonus

        if time_slot.value in ("evening", "late_night"):
            place_text = " ".join([place.name, *place.keywords]).lower()
            if any(sig in place_text for sig in NIGHTLIFE_SIGNALS):
                score += 0.5
        return score

    def _is_time_inappropriate(self, place: Place, time_slot: TimeSlot) -> bool:
        """낮 시간대에 야간 업소가 포함되어 있으면 True."""
        if time_slot.value not in ("morning", "lunch", "afternoon"):
            return False
        place_text = " ".join([place.name, *place.keywords]).lower()
        return any(sig in place_text for sig in NIGHTLIFE_SIGNALS)

    def rank_courses(
        self,
        courses: list[Course],
    ) -> tuple[Course | None, Course | None, Course | None]:
        if not courses:
            return None, None, None

        main = self._assign_type(
            max(courses, key=lambda course: (course.total_score, len(course.places))),
            "main",
        )

        remaining = [course for course in courses if course is not main]
        sub1 = self._pick_diverse_course(main, remaining, "sub1")

        remaining = [course for course in remaining if course is not sub1]
        anchors = [course for course in (main, sub1) if course is not None]
        sub2 = self._pick_diverse_multi_anchor(anchors, remaining, "sub2")

        return main, sub1, sub2

    def _assign_type(self, course: Course, course_type: str) -> Course:
        course.course_type = course_type
        return course

    def _pick_diverse_course(
        self,
        anchor: Course,
        candidates: list[Course],
        course_type: str,
    ) -> Course | None:
        if not candidates:
            return None

        strict = [candidate for candidate in candidates if not self._is_near_duplicate(anchor, candidate)]
        pool = strict if strict else candidates
        best = max(pool, key=lambda candidate: self._single_anchor_sort_key(anchor, candidate))
        return self._assign_type(best, course_type)

    def _pick_diverse_multi_anchor(
        self,
        anchors: list[Course],
        candidates: list[Course],
        course_type: str,
    ) -> Course | None:
        if not candidates:
            return None
        if not anchors:
            return self._assign_type(max(candidates, key=lambda course: course.total_score), course_type)

        strict = [
            candidate
            for candidate in candidates
            if not any(self._is_near_duplicate(anchor, candidate) for anchor in anchors)
        ]
        pool = strict if strict else candidates
        best = max(pool, key=lambda candidate: self._multi_anchor_sort_key(anchors, candidate))
        return self._assign_type(best, course_type)

    def _single_anchor_sort_key(self, anchor: Course, candidate: Course) -> tuple[float, float]:
        return (-self._overlap_penalty(anchor, candidate), candidate.total_score)

    def _multi_anchor_sort_key(self, anchors: list[Course], candidate: Course) -> tuple[float, float, float]:
        penalties = [self._overlap_penalty(anchor, candidate) for anchor in anchors]
        worst_penalty = max(penalties) if penalties else 0.0
        total_penalty = sum(penalties)
        return (-worst_penalty, -total_penalty, candidate.total_score)

    def _is_near_duplicate(self, anchor: Course, candidate: Course) -> bool:
        place_overlap = len(anchor.place_name_set() & candidate.place_name_set())
        if place_overlap >= 2:
            return True
        if anchor.first_place_name() == candidate.first_place_name():
            return True
        return False

    def _overlap_penalty(self, anchor: Course, candidate: Course) -> float:
        place_overlap_count = len(anchor.place_name_set() & candidate.place_name_set())
        category_overlap_count = len(anchor.category_set() & candidate.category_set())
        same_pattern = 1 if anchor.category_order() == candidate.category_order() else 0
        same_activity_subtype_count = self._shared_activity_subtype_count(anchor, candidate)
        return (
            place_overlap_count * 10.0
            + category_overlap_count * 2.0
            + same_pattern * 3.0
            + same_activity_subtype_count * 2.5
        )

    def _shared_activity_subtype_count(self, anchor: Course, candidate: Course) -> int:
        anchor_subtypes = {
            course_place.place.activity_subtype
            for course_place in anchor.places
            if course_place.place.activity_subtype
        }
        candidate_subtypes = {
            course_place.place.activity_subtype
            for course_place in candidate.places
            if course_place.place.activity_subtype
        }
        return len(anchor_subtypes & candidate_subtypes)
