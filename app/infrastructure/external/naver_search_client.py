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

    async def search_places(self, area: str, category: str, display: int = 10) -> list[dict]:
        """Naver 지역 검색 API — 장소 후보 수집"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_BASE_URL}/local.json",
                headers=self._headers,
                params={"query": area, "display": display, "sort": "comment"},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("items", [])

    async def search_images(self, query: str, display: int = 5) -> list[dict]:
        """Naver 이미지 검색 API"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_BASE_URL}/image.json",
                headers=self._headers,
                params={"query": query, "display": display},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("items", [])

    async def search_parking(self, address: str) -> bool:
        """차량 이동 시 — 주소 인근 500m 내 주차장 유무 확인"""
        if not address:
            return False
        area = " ".join(address.split()[:3])  # 시/구/동 단위까지만
        query = f"{area} {_PARKING_KEYWORD}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_BASE_URL}/local.json",
                headers=self._headers,
                params={"query": query, "display": 1},
                timeout=10.0,
            )
            resp.raise_for_status()
            return bool(resp.json().get("items"))
