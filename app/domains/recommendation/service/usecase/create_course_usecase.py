from __future__ import annotations

import html
import re
from datetime import time

from app.domains.recommendation.domain.entity.course import Course
from app.domains.recommendation.domain.entity.place import Place
from app.domains.recommendation.domain.service.course_composer import CourseComposer
from app.domains.recommendation.domain.service.rule_scorer import RuleScorer
from app.domains.recommendation.domain.service.time_slot_filter import TimeSlotFilter
from app.domains.recommendation.domain.value_object.time_slot import TimeSlot
from app.domains.recommendation.domain.value_object.transport import Transport
from app.domains.recommendation.service.dto.request.create_course_request_dto import CreateCourseRequestDto
from app.domains.recommendation.service.dto.response.create_course_response_dto import (
    CourseResultDto,
    CreateCourseResponseDto,
    PlaceResultDto,
)
from app.domains.recommendation.service.port.naver_datalab_port import NaverDatalabPort
from app.domains.recommendation.service.port.naver_search_port import NaverSearchPort

_INSUFFICIENT_MESSAGE = (
    "선택한 조건에 맞는 데이트 코스가 부족합니다. "
    "시간대나 지역을 변경하면 더 많은 추천을 받을 수 있습니다."
)

_IMAGE_EXCLUDE_KEYWORDS = frozenset({"협찬", "광고", "제공받아", "부동산", "분양"})
_BOLD_RE = re.compile(r"</?b>")

ALL_CATEGORIES = ["restaurant", "cafe", "walk", "activity"]

CATEGORY_IMAGE_SUFFIX = {
    "restaurant": "음식 사진",
    "cafe": "카페 외관",
    "walk": "산책로",
    "activity": "체험",
}

CATEGORY_NAVER_KEYWORD = {
    "restaurant": "맛집 음식점",
    "cafe": "카페",
    "walk": "산책로 공원",
    "activity": "이색데이트 체험",
}

# Datalab 쿼리용: {area} + 아래 키워드 조합으로 카테고리별 인기도 수집
CATEGORY_TREND_KEYWORD = {
    "restaurant": "맛집",
    "cafe": "카페",
    "walk": "산책",
    "activity": "이색체험",
}


class CreateCourseUseCase:

    def __init__(self, naver_search: NaverSearchPort, naver_datalab: NaverDatalabPort) -> None:
        self._search = naver_search
        self._datalab = naver_datalab
        self._slot_filter = TimeSlotFilter()
        self._scorer = RuleScorer()
        self._composer = CourseComposer()

    async def execute(self, dto: CreateCourseRequestDto) -> CreateCourseResponseDto:
        start_time = self._parse_time(dto.start_time)
        time_slot = TimeSlot.from_time(start_time)
        transport = Transport.from_str(dto.transport)

        # 1. 카테고리별 트렌드 수집 — 장소 후보 수집량 결정 기준
        category_trends = await self._collect_category_trends(dto.area)

        # 2. 트렌드 기반 장소 후보 수집 (트렌딩 카테고리 → 더 많은 후보)
        places_by_category = await self._collect_places(dto.area, category_trends)

        # 3. 시간대 필터링 (Domain Service)
        filtered = {
            cat: self._slot_filter.filter(places, time_slot)
            for cat, places in places_by_category.items()
        }

        # 4. 이미지 보강
        for cat, places in filtered.items():
            for place in places:
                place.image_url = await self._fetch_image(place, cat)

        # 5. 수집된 트렌드 점수 반영 (rating에 가산 → scoring 기준으로만 활용)
        self._apply_trend_scores(filtered, category_trends)

        # 6. 차량 이동 시 주차 정보 조회
        if transport.requires_parking_check():
            for places in filtered.values():
                for place in places:
                    place.has_parking = await self._search.search_parking(place.road_address)

        # 7. 코스 조합 (Domain Service)
        courses = self._composer.compose(filtered, time_slot, transport, start_time)

        # 8. Rule Scoring으로 메인/서브 순위 결정
        main, sub1, sub2 = self._scorer.rank_courses(courses)

        return self._build_response(main, sub1, sub2, time_slot, len(courses))

    # ── 트렌드 수집 ───────────────────────────────────────────────────────────

    async def _collect_category_trends(self, area: str) -> dict[str, float]:
        """Datalab으로 지역별 카테고리 트렌드 사전 수집 — 장소 후보 수집량 결정에 사용"""
        keywords = [f"{area} {CATEGORY_TREND_KEYWORD[cat]}" for cat in ALL_CATEGORIES]
        try:
            scores = await self._datalab.get_trend_scores(keywords[:5])
            return {
                cat: scores.get(f"{area} {CATEGORY_TREND_KEYWORD[cat]}", 0.0)
                for cat in ALL_CATEGORIES
            }
        except Exception:
            return {cat: 0.0 for cat in ALL_CATEGORIES}

    # ── 장소 수집 ─────────────────────────────────────────────────────────────

    async def _collect_places(
        self, area: str, category_trends: dict[str, float]
    ) -> dict[str, list[Place]]:
        """트렌드 점수가 높은 카테고리일수록 더 많은 후보 수집 (5~20개)"""
        result: dict[str, list[Place]] = {}
        for cat in ALL_CATEGORIES:
            trend_score = category_trends.get(cat, 0.0)
            display = max(5, min(20, int(10 + trend_score * 10)))
            keyword = CATEGORY_NAVER_KEYWORD[cat]
            raw = await self._search.search_places(f"{area} {keyword}", cat, display=display)
            result[cat] = [self._to_place(item, cat, rank) for rank, item in enumerate(raw, 1)]
        return result

    def _to_place(self, item: dict, category: str, rank: int) -> Place:
        name = _BOLD_RE.sub("", html.unescape(item.get("title", "")))
        desc = html.unescape(item.get("description", ""))
        road_addr = item.get("roadAddress", "")
        area_name = road_addr.split(" ")[1] if len(road_addr.split(" ")) > 1 else road_addr.split(" ")[0]

        # mapx/mapy: WGS84 × 10^7
        lat = int(item.get("mapy", 0)) / 1e7
        lng = int(item.get("mapx", 0)) / 1e7

        raw_category = item.get("category", "")
        keywords = [k.strip() for k in raw_category.split(">") if k.strip()]

        has_parking = "주차" in desc or "주차" in raw_category

        return Place(
            name=name,
            area=area_name,
            category=category,
            address=item.get("address", ""),
            road_address=road_addr,
            latitude=lat,
            longitude=lng,
            search_rank=rank,
            keywords=keywords,
            main_description=desc,
            brief_description=desc[:60] if desc else "",
            telephone=item.get("telephone", ""),
            has_parking=has_parking,
        )

    # ── 이미지 ────────────────────────────────────────────────────────────────

    async def _fetch_image(self, place: Place, category: str) -> str | None:
        suffix = CATEGORY_IMAGE_SUFFIX[category]
        query = f"{place.area} {place.name} {suffix}"
        images = await self._search.search_images(query)
        for img in images:
            if self._is_valid_image(img):
                return img.get("link") or img.get("thumbnail")
        return None

    def _is_valid_image(self, img: dict) -> bool:
        title = html.unescape(img.get("title", "")).lower()
        return not any(kw in title for kw in _IMAGE_EXCLUDE_KEYWORDS)

    # ── Datalab 트렌드 반영 ───────────────────────────────────────────────────

    def _apply_trend_scores(
        self,
        places_by_category: dict[str, list[Place]],
        category_trends: dict[str, float],
    ) -> None:
        """사전 수집된 트렌드 점수를 카테고리 단위로 장소 rating에 반영 (정렬 기준으로만 사용)"""
        for cat, places in places_by_category.items():
            category_trend = category_trends.get(cat, 0.0)
            for place in places:
                place.rating = min(5.0, place.rating + category_trend * 2.5)

    # ── 응답 변환 ─────────────────────────────────────────────────────────────

    def _build_response(
        self,
        main: Course | None,
        sub1: Course | None,
        sub2: Course | None,
        time_slot: TimeSlot,
        total_courses: int,
    ) -> CreateCourseResponseDto:
        message = _INSUFFICIENT_MESSAGE if total_courses < 3 else None
        sub_courses = [
            self._to_course_dto(c, time_slot) for c in [sub1, sub2] if c is not None
        ]
        return CreateCourseResponseDto(
            main_course=self._to_course_dto(main, time_slot) if main else None,
            sub_courses=sub_courses,
            message=message,
        )

    def _to_course_dto(self, course: Course, time_slot: TimeSlot) -> CourseResultDto:
        places = [
            PlaceResultDto(
                visit_order=cp.visit_order,
                name=cp.place.name,
                area=cp.place.area,
                category=cp.place.category,
                image_url=cp.place.image_url,
                main_description=cp.place.main_description,
                brief_description=cp.place.brief_description,
                keywords=[f"#{k}" for k in cp.place.keywords],
                estimated_duration_minutes=cp.estimated_duration_minutes,
                travel_time_to_next_minutes=cp.travel_time_to_next_minutes,
                recommended_time_slot=time_slot.value,
                has_parking=cp.place.has_parking if course.transport == "car" else None,
            )
            for cp in course.places
        ]
        return CourseResultDto(
            course_type=course.course_type,
            transport=course.transport,
            total_duration_minutes=course.total_duration_minutes(),
            places=places,
        )

    # ── 유틸 ──────────────────────────────────────────────────────────────────

    def _parse_time(self, time_str: str) -> time:
        try:
            h, m = map(int, time_str.split(":"))
            return time(h, m)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"시간 형식이 올바르지 않습니다: {time_str}") from e
