from __future__ import annotations

from app.domains.recommendation.domain.entity.place import Place
from app.domains.recommendation.domain.value_object.category import (
    CategoryType,
    LATE_NIGHT_RESTAURANT_KEYWORDS,
    LATE_NIGHT_CAFE_KEYWORDS,
    LATE_NIGHT_ACTIVITY_KEYWORDS,
)
from app.domains.recommendation.domain.value_object.time_slot import TimeSlot, TimeSlotType


class TimeSlotFilter:

    def filter(self, places: list[Place], time_slot: TimeSlot) -> list[Place]:
        return [
            p for p in places
            if self._is_category_allowed(p, time_slot.slot_type)
            and p.is_open_at_slot_start(time_slot.get_start_time())
        ]

    def _is_category_allowed(self, place: Place, slot_type: TimeSlotType) -> bool:
        kw = frozenset(place.keywords)

        if place.category == CategoryType.RESTAURANT.value:
            if slot_type == TimeSlotType.MORNING:
                return False
            if slot_type == TimeSlotType.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_RESTAURANT_KEYWORDS)
            return True

        if place.category == CategoryType.CAFE.value:
            if slot_type == TimeSlotType.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_CAFE_KEYWORDS)
            return True

        if place.category == CategoryType.WALK.value:
            return slot_type != TimeSlotType.LATE_NIGHT

        if place.category == CategoryType.ACTIVITY.value:
            if slot_type in (TimeSlotType.MORNING, TimeSlotType.LUNCH):
                return False
            if slot_type == TimeSlotType.LATE_NIGHT:
                return bool(kw & LATE_NIGHT_ACTIVITY_KEYWORDS)
            return True

        return False
