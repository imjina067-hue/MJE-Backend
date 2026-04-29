from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.recommendation.domain.value_object.time_slot import TimeSlotType


class CategoryType(str, Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    WALK = "walk"
    ACTIVITY = "activity"


LATE_NIGHT_RESTAURANT_KEYWORDS: frozenset[str] = frozenset({"술집", "포차", "야식", "심야"})
LATE_NIGHT_CAFE_KEYWORDS: frozenset[str] = frozenset({"심야카페", "24시카페"})
LATE_NIGHT_ACTIVITY_KEYWORDS: frozenset[str] = frozenset({"영화관", "볼링장", "노래방"})


@dataclass(frozen=True)
class Category:
    category_type: CategoryType

    @classmethod
    def from_str(cls, value: str) -> Category:
        return cls(CategoryType(value))

    def is_allowed_for_slot(self, slot_type: TimeSlotType, keywords: frozenset[str] | None = None) -> bool:
        from app.domains.recommendation.domain.value_object.time_slot import TimeSlotType as ST
        kw = keywords or frozenset()

        if self.category_type == CategoryType.RESTAURANT:
            if slot_type == ST.MORNING:
                return False
            if slot_type == ST.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_RESTAURANT_KEYWORDS)
            return True

        if self.category_type == CategoryType.CAFE:
            if slot_type == ST.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_CAFE_KEYWORDS)
            return True

        if self.category_type == CategoryType.WALK:
            return slot_type != ST.LATE_NIGHT

        if self.category_type == CategoryType.ACTIVITY:
            if slot_type in (ST.MORNING, ST.LUNCH):
                return False
            if slot_type == ST.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_ACTIVITY_KEYWORDS)
            return True

        return False

    def default_duration_minutes(self) -> int:
        durations = {
            CategoryType.RESTAURANT: 90,
            CategoryType.CAFE: 60,
            CategoryType.WALK: 90,
            CategoryType.ACTIVITY: 120,
        }
        return durations[self.category_type]

    def naver_search_keyword(self) -> str:
        keywords = {
            CategoryType.RESTAURANT: "맛집 음식점",
            CategoryType.CAFE: "카페",
            CategoryType.WALK: "산책로 공원",
            CategoryType.ACTIVITY: "이색데이트 체험",
        }
        return keywords[self.category_type]

    def image_search_suffix(self) -> str:
        suffixes = {
            CategoryType.RESTAURANT: "음식 사진",
            CategoryType.CAFE: "카페 외관",
            CategoryType.WALK: "산책로",
            CategoryType.ACTIVITY: "체험",
        }
        return suffixes[self.category_type]

    @property
    def value(self) -> str:
        return self.category_type.value
