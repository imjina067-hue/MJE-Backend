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

        sorted_courses = sorted(courses, key=lambda c: c.total_score, reverse=True)
        main = self._assign_type(sorted_courses[0], "main")

        remaining = [course for course in sorted_courses[1:] if course is not main]
        sub1 = self._pick_diverse_course(main, remaining, "sub1")

        remaining = [course for course in remaining if course is not sub1]
        anchors = [course for course in [main, sub1] if course is not None]
        sub2 = self._pick_diverse_course_multi_anchor(anchors, remaining, "sub2")

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

        best = max(
            candidates,
            key=lambda candidate: self._diversity_sort_key(anchor, candidate),
        )
        return self._assign_type(best, course_type)

    def _pick_diverse_course_multi_anchor(
        self,
        anchors: list[Course],
        candidates: list[Course],
        course_type: str,
    ) -> Course | None:
        if not candidates:
            return None

        best = max(
            candidates,
            key=lambda candidate: self._multi_anchor_diversity_key(anchors, candidate),
        )
        return self._assign_type(best, course_type)

    def _diversity_sort_key(self, anchor: Course, candidate: Course) -> tuple[float, float]:
        overlap_penalty = self._overlap_penalty(anchor, candidate)
        return (-overlap_penalty, candidate.total_score)

    def _multi_anchor_diversity_key(
        self,
        anchors: list[Course],
        candidate: Course,
    ) -> tuple[float, float]:
        if not anchors:
            return (0.0, candidate.total_score)

        penalties = [self._overlap_penalty(anchor, candidate) for anchor in anchors]
        worst_penalty = max(penalties)
        total_penalty = sum(penalties)
        return (-worst_penalty, -total_penalty, candidate.total_score)

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
