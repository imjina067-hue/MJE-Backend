from __future__ import annotations

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place


class RuleScorer:

    def score_places(self, places: list[Place]) -> list[tuple[Place, float]]:
        """검색순위 + 별점 합산 점수로 장소 정렬"""
        total = len(places)
        scored = [(p, p.calculate_total_score(total)) for p in places]
        return sorted(scored, key=lambda x: x[1], reverse=True)

    def rank_courses(
        self, courses: list[Course]
    ) -> tuple[Course | None, Course | None, Course | None]:
        """총점 기준으로 메인 → 서브1 → 서브2 순위 부여"""
        if not courses:
            return None, None, None

        sorted_courses = sorted(courses, key=lambda c: c.total_score, reverse=True)

        main = self._assign_type(sorted_courses, 0, "main")
        sub1 = self._assign_type(sorted_courses, 1, "sub1")
        sub2 = self._assign_type(sorted_courses, 2, "sub2")
        return main, sub1, sub2

    def _assign_type(
        self, courses: list[Course], idx: int, course_type: str
    ) -> Course | None:
        if idx >= len(courses):
            return None
        courses[idx].course_type = course_type
        return courses[idx]
