from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.courses.repository.event_repository_impl import EventRepositoryImpl as CoursesEventRepositoryImpl
from app.domains.courses.service.usecase.track_event_usecase import TrackEventUseCase as CoursesTrackEventUseCase
from app.infrastructure.api.repository.export_log_repository_impl import ExportLogRepositoryImpl
from app.infrastructure.api.service.usecase.track_export_event_usecase import TrackExportEventUseCase
from app.domains.home.repository.event_repository_impl import EventRepositoryImpl as HomeEventRepositoryImpl
from app.domains.home.service.usecase.track_event_usecase import TrackEventUseCase as HomeTrackEventUseCase
from app.domains.recommendation.repository.course_detail_repository_impl import CourseDetailRepositoryImpl
from app.domains.recommendation.service.usecase.create_course_usecase import CreateCourseUseCase
from app.domains.recommendation.service.usecase.get_course_detail_usecase import GetCourseDetailUseCase
from app.infrastructure.api.service.usecase.send_email_usecase import SendEmailUseCase
from app.infrastructure.database.session import get_db_session
from app.infrastructure.external.email_client import EmailClient
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


def get_home_track_event_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> HomeTrackEventUseCase:
    return HomeTrackEventUseCase(event_repository=HomeEventRepositoryImpl(session=session))


def get_courses_track_event_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> CoursesTrackEventUseCase:
    return CoursesTrackEventUseCase(event_repository=CoursesEventRepositoryImpl(session=session))


def get_export_track_event_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> TrackExportEventUseCase:
    return TrackExportEventUseCase(repository=ExportLogRepositoryImpl(session=session))


@lru_cache
def _email_client() -> EmailClient:
    return EmailClient()


def get_send_email_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> SendEmailUseCase:
    return SendEmailUseCase(
        course_repository=CourseDetailRepositoryImpl(session=session),
        email_port=_email_client(),
    )


def get_course_detail_usecase(
    session: AsyncSession = Depends(get_db_session),
) -> GetCourseDetailUseCase:
    return GetCourseDetailUseCase(course_detail_repository=CourseDetailRepositoryImpl(session=session))
