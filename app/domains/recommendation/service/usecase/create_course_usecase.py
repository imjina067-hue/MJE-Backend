from __future__ import annotations

import html
import logging
import re
import uuid
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
from app.domains.recommendation.service.port.course_store_port import CourseStorePort
from app.domains.recommendation.service.port.naver_datalab_port import NaverDatalabPort
from app.domains.recommendation.service.port.naver_map_port import NaverMapPort
from app.domains.recommendation.service.port.naver_search_port import NaverSearchPort

_INSUFFICIENT_MESSAGE = (
    "선택한 조건에 맞는 데이트 코스가 부족합니다. "
    "시간대나 지역을 변경하면 더 많은 추천을 받을 수 있습니다."
)

_IMAGE_EXCLUDE_KEYWORDS = frozenset({"협찬", "광고", "제공받아", "부동산", "분양"})
_IMAGE_HARD_EXCLUDE_KEYWORDS = frozenset(
    {"map", "logo", "banner", "poster", "ad", "guide", "capture"}
)
_BOLD_RE = re.compile(r"</?b>")

ALL_CATEGORIES = ["restaurant", "cafe", "walk", "activity"]

_CATEGORY_SIGNALS: dict[str, tuple[str, ...]] = {
    "restaurant": ("음식", "식당", "맛집", "요리", "주점", "술집", "포차", "바", "레스토랑"),
    "cafe": ("카페", "커피", "디저트", "베이커리", "브런치"),
    "walk": ("공원", "산책", "거리", "둘레길", "하천", "호수", "전망", "야경", "광장"),
    "activity": ("전시", "체험", "공방", "영화", "볼링", "방탈출", "노래방", "갤러리", "스튜디오"),
}

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


logger = logging.getLogger(__name__)


class CreateCourseUseCase:

    def __init__(
        self,
        naver_search: NaverSearchPort,
        naver_datalab: NaverDatalabPort,
        naver_map: NaverMapPort,
        course_store: CourseStorePort,
    ) -> None:
        self._search = naver_search
        self._datalab = naver_datalab
        self._map = naver_map
        self._course_store = course_store
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
        self._log_recommendation_diagnostics(
            dto=dto,
            time_slot=time_slot,
            transport=transport,
            places_by_category=places_by_category,
            filtered_places=filtered,
            courses=courses,
        )

        # 8. Rule Scoring으로 메인/서브 순위 결정
        main, sub1, sub2 = self._scorer.rank_courses(courses)

        # 9. 최종 코스에 한해 Naver 지도 API로 실제 이동소요시간·동선 보강
        final_courses = [c for c in [main, sub1, sub2] if c is not None]
        await self._enrich_with_routes(final_courses, dto.transport)

        recommendation_id = str(uuid.uuid4())
        response = self._build_response(
            main,
            sub1,
            sub2,
            time_slot,
            len(courses),
            recommendation_id,
        )
        self._course_store.save(recommendation_id, response)
        return response

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
            candidates = [self._to_place(item, cat, rank) for rank, item in enumerate(raw, 1)]
            result[cat] = self._sanitize_places(area, cat, candidates)
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

    def _sanitize_places(self, requested_area: str, category: str, places: list[Place]) -> list[Place]:
        sanitized: list[Place] = []
        seen_keys: set[tuple[str, str]] = set()
        dropped_counts = {
            "invalid_coordinate": 0,
            "area_mismatch": 0,
            "duplicate": 0,
            "category_mismatch": 0,
        }

        for place in places:
            if not self._has_valid_coordinates(place):
                dropped_counts["invalid_coordinate"] += 1
                continue

            if not self._matches_requested_area(requested_area, place):
                dropped_counts["area_mismatch"] += 1
                continue

            dedupe_key = self._place_dedupe_key(place)
            if dedupe_key in seen_keys:
                dropped_counts["duplicate"] += 1
                continue

            if not self._matches_category_signal(category, place):
                dropped_counts["category_mismatch"] += 1
                continue

            seen_keys.add(dedupe_key)
            sanitized.append(place)

        if any(dropped_counts.values()):
            logger.info(
                "recommendation.sanitize area=%s category=%s before=%s after=%s dropped=%s",
                requested_area,
                category,
                len(places),
                len(sanitized),
                dropped_counts,
            )

        return sanitized

    def _has_valid_coordinates(self, place: Place) -> bool:
        return not (
            abs(place.latitude) < 0.000001
            or abs(place.longitude) < 0.000001
            or not (-90 <= place.latitude <= 90)
            or not (-180 <= place.longitude <= 180)
        )

    def _matches_requested_area(self, requested_area: str, place: Place) -> bool:
        normalized_area = self._normalize_text(requested_area)
        if not normalized_area:
            return True

        haystack = self._normalize_text(
            " ".join(
                part
                for part in [place.area, place.address, place.road_address]
                if part
            )
        )
        if not haystack:
            return False

        return all(token in haystack for token in normalized_area.split())

    def _place_dedupe_key(self, place: Place) -> tuple[str, str]:
        normalized_name = self._normalize_text(place.name)
        normalized_address = self._normalize_text(place.road_address or place.address)
        return normalized_name, normalized_address

    def _matches_category_signal(self, category: str, place: Place) -> bool:
        signals = _CATEGORY_SIGNALS.get(category, ())
        if not signals:
            return True

        text = self._normalize_text(
            " ".join(
                [
                    place.name,
                    place.main_description,
                    place.brief_description,
                    " ".join(place.keywords),
                ]
            )
        )
        if not text:
            return True

        if any(signal in text for signal in signals):
            return True

        # 음식점은 카테고리 폭이 넓어서 너무 공격적으로 제외하지 않는다.
        if category == "restaurant":
            return True

        return False

    def _normalize_text(self, value: str) -> str:
        return " ".join(value.lower().split())

    # ── 이미지 ────────────────────────────────────────────────────────────────

    async def _fetch_image(self, place: Place, category: str) -> str | None:
        suffix = CATEGORY_IMAGE_SUFFIX[category]
        query = f"{place.area} {place.name} {suffix}"
        images = await self._search.search_images(query)
        best_url: str | None = None
        best_score: int | None = None
        for img in images:
            score = self._score_image_candidate(img, place, category)
            if score is None:
                continue
            image_url = img.get("link") or img.get("thumbnail")
            if not image_url:
                continue
            if best_score is None or score > best_score:
                best_score = score
                best_url = image_url
        return best_url

    def _is_valid_image(self, img: dict) -> bool:
        title = html.unescape(img.get("title", "")).lower()
        return not any(kw in title for kw in _IMAGE_EXCLUDE_KEYWORDS)

    def _score_image_candidate(self, img: dict, place: Place, category: str) -> int | None:
        title = self._normalize_text(html.unescape(img.get("title", "")))
        link = self._normalize_text(img.get("link", ""))
        combined = f"{title} {link}".strip()

        if not combined:
            return None
        if not self._is_valid_image(img):
            return None
        if any(keyword in combined for keyword in _IMAGE_HARD_EXCLUDE_KEYWORDS):
            return None

        score = 0
        place_name = self._normalize_text(place.name)
        area = self._normalize_text(place.area)

        if place_name and place_name in combined:
            score += 6
        else:
            name_tokens = [token for token in place_name.split() if len(token) >= 2]
            score += sum(2 for token in name_tokens if token in combined)

        if area and area in combined:
            score += 2

        category_signals = _CATEGORY_SIGNALS.get(category, ())
        score += sum(1 for signal in category_signals if self._normalize_text(signal) in combined)

        if any(bad in combined for bad in ("face", "selfie", "profile", "人物")):
            score -= 4

        return score if score > 0 else None

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

    # ── 지도 API 동선 보강 ─────────────────────────────────────────────────────

    async def _enrich_with_routes(self, courses: list[Course], transport: str) -> None:
        """랭킹된 최종 코스에 한해 Naver 지도 API로 실제 이동소요시간·경로 적용"""
        for course in courses:
            for i, cp in enumerate(course.places[:-1]):
                next_cp = course.places[i + 1]
                route = await self._map.get_directions(
                    cp.place.latitude, cp.place.longitude,
                    next_cp.place.latitude, next_cp.place.longitude,
                    transport,
                )
                if route is not None:
                    cp.travel_time_to_next_minutes = route.duration_minutes
                    cp.route_path_to_next = route.path

    # ── 응답 변환 ─────────────────────────────────────────────────────────────

    def _build_response(
        self,
        main: Course | None,
        sub1: Course | None,
        sub2: Course | None,
        time_slot: TimeSlot,
        total_courses: int,
        recommendation_id: str,
    ) -> CreateCourseResponseDto:
        message = _INSUFFICIENT_MESSAGE if total_courses < 3 else None
        sub_courses = [
            self._to_course_dto(c, time_slot, str(uuid.uuid4())) for c in [sub1, sub2] if c is not None
        ]
        return CreateCourseResponseDto(
            course_id=recommendation_id,
            main_course=self._to_course_dto(main, time_slot, str(uuid.uuid4())) if main else None,
            sub_courses=sub_courses,
            message=message,
        )

    def _to_course_dto(self, course: Course, time_slot: TimeSlot, course_id: str) -> CourseResultDto:
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
                route_path_to_next=cp.route_path_to_next,
            )
            for cp in course.places
        ]
        return CourseResultDto(
            course_id=course_id,
            course_type=course.course_type,
            transport=course.transport,
            total_duration_minutes=course.total_duration_minutes(),
            places=places,
        )

    # ── 유틸 ──────────────────────────────────────────────────────────────────

    def _log_recommendation_diagnostics(
        self,
        dto: CreateCourseRequestDto,
        time_slot: TimeSlot,
        transport: Transport,
        places_by_category: dict[str, list[Place]],
        filtered_places: dict[str, list[Place]],
        courses: list[Course],
    ) -> None:
        raw_counts = {category: len(places) for category, places in places_by_category.items()}
        filtered_counts = {category: len(places) for category, places in filtered_places.items()}
        empty_after_filter = [
            category for category, count in filtered_counts.items() if count == 0
        ]
        populated_categories = [
            category for category, count in filtered_counts.items() if count > 0
        ]

        if len(courses) >= 3:
            logger.info(
                "recommendation.generated area=%s time_slot=%s transport=%s raw_counts=%s filtered_counts=%s course_count=%s",
                dto.area,
                time_slot.value,
                transport.value,
                raw_counts,
                filtered_counts,
                len(courses),
            )
            return

        reason_codes: list[str] = []
        if not populated_categories:
            reason_codes.append("no_places_after_filter")
        elif len(populated_categories) == 1:
            reason_codes.append("single_category_remaining")
        elif len(courses) == 0:
            reason_codes.append("composition_failed")
        if len(courses) < 3:
            reason_codes.append("insufficient_course_count")
        if empty_after_filter:
            reason_codes.append("category_exhausted_after_filter")

        logger.warning(
            "recommendation.insufficient area=%s start_time=%s time_slot=%s transport=%s raw_counts=%s filtered_counts=%s empty_after_filter=%s populated_categories=%s course_count=%s reason_codes=%s",
            dto.area,
            dto.start_time,
            time_slot.value,
            transport.value,
            raw_counts,
            filtered_counts,
            empty_after_filter,
            populated_categories,
            len(courses),
            reason_codes,
        )

    def _parse_time(self, time_str: str) -> time:
        try:
            h, m = map(int, time_str.split(":"))
            return time(h, m)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"시간 형식이 올바르지 않습니다: {time_str}") from e
