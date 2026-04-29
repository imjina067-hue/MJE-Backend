from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class TransportType(str, Enum):
    CAR = "car"
    WALK = "walk"
    PUBLIC_TRANSIT = "public_transit"


@dataclass(frozen=True)
class Transport:
    transport_type: TransportType

    MAX_TRAVEL_MINUTES: ClassVar[dict[TransportType, int]] = {
        TransportType.CAR: 30,
        TransportType.WALK: 10,
        TransportType.PUBLIC_TRANSIT: 20,
    }

    # 이동 속도 (m/s)
    SPEED_MPS: ClassVar[dict[TransportType, float]] = {
        TransportType.CAR: 8.33,       # 시내 약 30km/h
        TransportType.WALK: 1.39,       # 약 5km/h
        TransportType.PUBLIC_TRANSIT: 5.0,  # 약 18km/h 평균
    }

    CAR_PARKING_RADIUS_METERS: ClassVar[int] = 500

    @classmethod
    def from_str(cls, value: str) -> Transport:
        return cls(TransportType(value))

    def max_travel_minutes(self) -> int:
        return self.MAX_TRAVEL_MINUTES[self.transport_type]

    def speed_mps(self) -> float:
        return self.SPEED_MPS[self.transport_type]

    def requires_parking_check(self) -> bool:
        return self.transport_type == TransportType.CAR

    @property
    def value(self) -> str:
        return self.transport_type.value
