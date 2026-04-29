from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


@dataclass
class RouteResult:
    duration_minutes: int
    distance_meters: int
    path: list[tuple[float, float]] = field(default_factory=list)  # [(lat, lng), ...]


@runtime_checkable
class NaverMapPort(Protocol):
    async def get_directions(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        transport: str,
    ) -> Optional[RouteResult]: ...
