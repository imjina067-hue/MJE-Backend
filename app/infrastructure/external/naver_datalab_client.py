from __future__ import annotations

from datetime import date, timedelta

import httpx

from app.infrastructure.config.settings import get_settings

_BASE_URL = "https://openapi.naver.com/v1/datalab/search"


class NaverDatalabClient:

    def __init__(self) -> None:
        settings = get_settings()
        self._headers = {
            "X-Naver-Client-Id": settings.NAVER_DATALAB_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_DATALAB_CLIENT_SECRET,
            "Content-Type": "application/json",
        }

    async def get_trend_scores(self, keywords: list[str]) -> dict[str, float]:
        """최근 30일 검색 트렌드 — 0~1 사이로 정규화하여 반환"""
        if not keywords:
            return {}

        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in keywords[:5]]

        payload = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "timeUnit": "month",
            "keywordGroups": keyword_groups,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _BASE_URL,
                headers=self._headers,
                json=payload,
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()

        result: dict[str, float] = {}
        for item in data.get("results", []):
            keyword = item.get("title", "")
            data_points = item.get("data", [])
            if data_points:
                avg = sum(d.get("ratio", 0) for d in data_points) / len(data_points)
                result[keyword] = avg / 100.0
        return result
