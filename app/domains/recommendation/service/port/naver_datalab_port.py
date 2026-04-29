from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class NaverDatalabPort(Protocol):
    async def get_trend_scores(self, keywords: list[str]) -> dict[str, float]: ...
