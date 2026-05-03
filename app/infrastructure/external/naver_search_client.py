from __future__ import annotations

import httpx

from app.infrastructure.config.settings import get_settings

_BASE_URL = "https://openapi.naver.com/v1/search"
_PARKING_KEYWORD = "주차장"


class NaverSearchClient:

    def __init__(self) -> None:
        settings = get_settings()
        self._headers = {
            "X-Naver-Client-Id": settings.NAVER_SEARCH_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_SEARCH_CLIENT_SECRET,
        }
        self._client = httpx.AsyncClient(timeout=10.0)

    async def search_places(self, area: str, category: str, display: int = 10) -> list[dict]:
        """Collect place candidates from the Naver local search API."""
        resp = await self._client.get(
            f"{_BASE_URL}/local.json",
            headers=self._headers,
            params={"query": area, "display": display, "sort": "comment"},
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def search_images(self, query: str, display: int = 5) -> list[dict]:
        """Search image candidates from the Naver image search API."""
        resp = await self._client.get(
            f"{_BASE_URL}/image.json",
            headers=self._headers,
            params={"query": query, "display": display},
        )
        resp.raise_for_status()
        return resp.json().get("items", [])

    async def search_parking(self, address: str) -> bool:
        """Check whether nearby parking results exist for the given address."""
        if not address:
            return False

        area = " ".join(address.split()[:3])
        query = f"{area} {_PARKING_KEYWORD}"
        resp = await self._client.get(
            f"{_BASE_URL}/local.json",
            headers=self._headers,
            params={"query": query, "display": 1},
        )
        resp.raise_for_status()
        return bool(resp.json().get("items"))

    async def aclose(self) -> None:
        await self._client.aclose()
