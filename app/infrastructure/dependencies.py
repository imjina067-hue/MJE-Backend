from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.recommendation.service.usecase.create_course_usecase import CreateCourseUseCase
from app.domains.tracking.repository.event_repository_impl import EventRepositoryImpl
from app.domains.tracking.service.usecase.track_event_usecase import TrackEventUseCase
from app.infrastructure.database.session import get_db_session
from app.infrastructure.external.naver_datalab_client import NaverDatalabClient
from app.infrastructure.external.naver_map_client import NaverMapClient
from app.infrastructure.external.naver_search_client import NaverSearchClient


@lru_cache
def _naver_search_client() -> NaverSearchClient:
    return NaverSearchClient()


@lru_cache
def _naver_datalab_client() -> NaverDatalabClient:
    return NaverDatalabClient()


@lru_cache
def _naver_map_client() -> NaverMapClient:
    return NaverMapClient()


def get_create_course_usecase() -> CreateCourseUseCase:
    return CreateCourseUseCase(
        naver_search=_naver_search_client(),
        naver_datalab=_naver_datalab_client(),
        naver_map=_naver_map_client(),
    )


def get_track_event_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> TrackEventUseCase:
    return TrackEventUseCase(event_repository=EventRepositoryImpl(session=session))
