from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import time
from typing import Optional


@dataclass
class Place:
    name: str
    area: str
    category: str           # "restaurant" | "cafe" | "walk" | "activity"
    address: str
    road_address: str
    latitude: float
    longitude: float
    search_rank: int        # Naver 검색 결과 내 순위 (1-based)

    keywords: list[str] = field(default_factory=list)
    main_description: str = ""
    brief_description: str = ""
    telephone: str = ""
    image_url: Optional[str] = None
    rating: float = 0.0
    has_parking: bool = False
    business_close_time: Optional[time] = None

    def is_open_at_slot_start(self, slot_start: time) -> bool:
        """영업 종료가 슬롯 시작 기준 1시간 이내이면 False"""
        if self.business_close_time is None:
            return True
        close = self.business_close_time
        # 자정 이후 영업 종료 (예: 01:00) → 충분히 열려있다고 간주
        if close < time(2, 0):
            return True
        close_min = close.hour * 60 + close.minute
        start_min = slot_start.hour * 60 + slot_start.minute
        return (close_min - start_min) > 60

    def calculate_total_score(self, total_candidates: int) -> float:
        return self._search_rank_score(total_candidates) + self._rating_score()

    def _search_rank_score(self, total_candidates: int) -> float:
        if total_candidates <= 0 or self.search_rank <= 0:
            return 0.0
        return (total_candidates - self.search_rank + 1) / total_candidates * 100

    def _rating_score(self) -> float:
        if self.rating <= 0:
            return 0.0
        return (self.rating / 5.0) * 100

    def distance_to_meters(self, other: Place) -> float:
        """Haversine 공식으로 두 장소 간 거리(m) 계산"""
        R = 6_371_000
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return R * 2 * math.asin(math.sqrt(a))
