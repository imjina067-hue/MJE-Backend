from __future__ import annotations

from typing import Optional

import httpx

from app.domains.recommendation.service.port.naver_map_port import RouteResult
from app.infrastructure.config.settings import get_settings

_DRIVING_URL = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
_WALKING_URL = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/walking"

_TRANSPORT_URL = {
    "car": _DRIVING_URL,
    "walk": _WALKING_URL,
    "public_transit": _DRIVING_URL,
}

_ROUTE_KEY = {
    "car": "trafast",
    "walk": "traoptimal",
    "public_transit": "trafast",
}


class NaverMapClient:

    def __init__(self) -> None:
        settings = get_settings()
        self._client_id = settings.NAVER_MAP_CLIENT_ID
        self._client_secret = settings.NAVER_MAP_CLIENT_SECRET
        self._client = httpx.AsyncClient(timeout=10.0)

    def _is_configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    async def get_directions(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        transport: str,
    ) -> Optional[RouteResult]:
        if not self._is_configured():
            return None

        url = _TRANSPORT_URL.get(transport, _DRIVING_URL)
        route_key = _ROUTE_KEY.get(transport, "trafast")

        headers = {
            "X-NCP-APIGW-API-KEY-ID": self._client_id,
            "X-NCP-APIGW-API-KEY": self._client_secret,
        }
        params = {
            "start": f"{start_lng},{start_lat}",
            "goal": f"{end_lng},{end_lat}",
            "option": route_key,
        }

        try:
            resp = await self._client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None

        routes = data.get("route", {}).get(route_key, [])
        if not routes:
            return None

        summary = routes[0].get("summary", {})
        duration_ms = summary.get("duration", 0)
        distance_m = summary.get("distance", 0)
        raw_path = routes[0].get("path", [])
        path = [(lat, lng) for lng, lat in raw_path]

        return RouteResult(
            duration_minutes=max(1, int(duration_ms / 60_000)),
            distance_meters=int(distance_m),
            path=path,
        )

    async def aclose(self) -> None:
        await self._client.aclose()
