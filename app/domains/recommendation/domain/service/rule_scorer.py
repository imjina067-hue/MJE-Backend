from __future__ import annotations

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place


class RuleScorer:

    def score_places(self, places: list[Place]) -> list[tuple[Place, float]]:
        """Search rank and rating based place scoring."""
        total = len(places)
        scored = [(p, p.calculate_total_score(total)) for p in places]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def rank_courses(
        self, courses: list[Course]
    ) -> tuple[Course | None, Course | None, Course | None]:
        """Pick main first, then choose diverse sub courses."""
        if not courses:
            return None, None, None

        main = self._pick_main_course(courses)

        remaining = [c for c in courses if c is not main]
        sub1_candidates = [c for c in remaining if not self._is_too_similar(main, c)]
        sub1 = self._pick_sub1_course(main, sub1_candidates)

        remaining = [c for c in remaining if c is not sub1]
        anchors = [c for c in [main, sub1] if c is not None]
        sub2_candidates = [c for c in remaining if not any(self._is_too_similar(a, c) for a in anchors)]
        sub2 = self._pick_sub2_course(anchors, sub2_candidates)

        return main, sub1, sub2

    def _pick_main_course(self, courses: list[Course]) -> Course:
        """Highest total_score wins; more places breaks ties."""
        return self._assign_type(
            max(courses, key=lambda c: (c.total_score, len(c.places))),
            "main",
        )

    def _assign_type(self, course: Course, course_type: str) -> Course:
        course.course_type = course_type
        return course

    def _pick_sub1_course(self, main: Course, candidates: list[Course]) -> Course | None:
        if not candidates:
            return None
        strict = [c for c in candidates if not self._is_same_activity_type(main, c)]
        pool = strict if strict else candidates
        best = max(pool, key=lambda c: self._sub1_sort_key(main, c))
        return self._assign_type(best, "sub1")

    def _pick_sub2_course(self, anchors: list[Course], candidates: list[Course]) -> Course | None:
        if not candidates:
            return None
        strict = [c for c in candidates if not any(self._is_same_activity_type(a, c) for a in anchors)]
        pool = strict if strict else candidates
        best = max(pool, key=lambda c: self._sub2_sort_key(anchors, c))
        return self._assign_type(best, "sub2")

    def _sub2_sort_key(self, anchors: list[Course], candidate: Course) -> tuple:
        different_from_all = int(all(a.category_order() != candidate.category_order() for a in anchors))
        different_from_any = int(any(a.category_order() != candidate.category_order() for a in anchors))
        penalties = [self._overlap_penalty(a, candidate) for a in anchors]
        worst_penalty = max(penalties) if penalties else 0.0
        total_penalty = sum(penalties)
        return (different_from_all, different_from_any, -worst_penalty, -total_penalty, candidate.total_score)

    def _sub1_sort_key(self, main: Course, candidate: Course) -> tuple:
        different_pattern = 0 if main.category_order() == candidate.category_order() else 1
        penalty = self._overlap_penalty(main, candidate)
        return (different_pattern, -penalty, candidate.total_score)

    def _is_same_activity_type(self, anchor: Course, candidate: Course) -> bool:
        anchor_types = {cp.place.keywords[-1] for cp in anchor.places if cp.place.keywords}
        cand_types = {cp.place.keywords[-1] for cp in candidate.places if cp.place.keywords}
        return len(anchor_types & cand_types) >= 2

    def _is_too_similar(self, anchor: Course, candidate: Course) -> bool:
        place_overlap = len(anchor.place_name_set() & candidate.place_name_set())
        return place_overlap >= 2 or anchor.first_place_name() == candidate.first_place_name()

    def _overlap_penalty(self, anchor: Course, candidate: Course) -> float:
        anchor_places = anchor.place_name_set()
        candidate_places = candidate.place_name_set()
        place_overlap_count = len(anchor_places & candidate_places)

        anchor_categories = anchor.category_set()
        candidate_categories = candidate.category_set()
        category_overlap_count = len(anchor_categories & candidate_categories)

        shared_keyword_count = len(anchor.all_keywords() & candidate.all_keywords())
        same_first_place = 1 if anchor.first_place_name() == candidate.first_place_name() else 0

        return (
            place_overlap_count * 10.0
            + category_overlap_count * 2.0
            + shared_keyword_count * 0.2
            + same_first_place * 5.0
        )
