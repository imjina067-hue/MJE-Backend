from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class NaverSearchPort(Protocol):
    async def search_places(self, area: str, category: str, display: int = 10) -> list[dict]: ...
    async def search_images(self, query: str, display: int = 5) -> list[dict]: ...
    async def search_parking(self, address: str) -> bool: ...
