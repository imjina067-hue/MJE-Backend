from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import ClassVar


class TimeSlotType(str, Enum):
    MORNING = "morning"
    LUNCH = "lunch"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    LATE_NIGHT = "late_night"


@dataclass(frozen=True)
class TimeSlot:
    slot_type: TimeSlotType

    SLOT_START_TIMES: ClassVar[dict[TimeSlotType, time]] = {
        TimeSlotType.MORNING: time(9, 0),
        TimeSlotType.LUNCH: time(11, 30),
        TimeSlotType.AFTERNOON: time(14, 0),
        TimeSlotType.EVENING: time(17, 30),
        TimeSlotType.LATE_NIGHT: time(21, 30),
    }

    @classmethod
    def from_time(cls, t: time) -> TimeSlot:
        total = t.hour * 60 + t.minute
        if 9 * 60 <= total < 11 * 60 + 30:
            return cls(TimeSlotType.MORNING)
        if 11 * 60 + 30 <= total < 14 * 60:
            return cls(TimeSlotType.LUNCH)
        if 14 * 60 <= total < 17 * 60 + 30:
            return cls(TimeSlotType.AFTERNOON)
        if 17 * 60 + 30 <= total < 21 * 60 + 30:
            return cls(TimeSlotType.EVENING)
        if total >= 21 * 60 + 30 or total < 60:
            return cls(TimeSlotType.LATE_NIGHT)
        raise ValueError(f"서비스 가능 시간은 09:00 ~ 01:00입니다. 입력값: {t}")

    def get_start_time(self) -> time:
        return self.SLOT_START_TIMES[self.slot_type]

    def is_late_night(self) -> bool:
        return self.slot_type == TimeSlotType.LATE_NIGHT

    @property
    def value(self) -> str:
        return self.slot_type.value
