from __future__ import annotations

from functools import lru_cache

from app.domains.recommendation.service.usecase.create_course_usecase import CreateCourseUseCase
from app.infrastructure.external.naver_datalab_client import NaverDatalabClient
from app.infrastructure.external.naver_search_client import NaverSearchClient


@lru_cache
def _naver_search_client() -> NaverSearchClient:
    return NaverSearchClient()


@lru_cache
def _naver_datalab_client() -> NaverDatalabClient:
    return NaverDatalabClient()


def get_create_course_usecase() -> CreateCourseUseCase:
    return CreateCourseUseCase(
        naver_search=_naver_search_client(),
        naver_datalab=_naver_datalab_client(),
    )
