from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.courses.repository.orm.course_orm import CourseOrm
from app.domains.courses.repository.orm.course_place_orm import CoursePlaceOrm
from app.domains.recommendation.domain.entity.course_detail import CourseDetail, SubCourse
from app.domains.recommendation.repository.mapper.course_detail_mapper import CourseDetailMapper


class CourseDetailRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_course_id(self, course_id: str) -> Optional[CourseDetail]:
        course_result = await self._session.execute(
            select(CourseOrm).where(CourseOrm.course_id == course_id)
        )
        course_orm = course_result.scalar_one_or_none()
        if course_orm is None:
            return None

        places_result = await self._session.execute(
            select(CoursePlaceOrm)
            .where(CoursePlaceOrm.course_id == course_id)
            .order_by(CoursePlaceOrm.visit_order)
        )
        place_orms = list(places_result.scalars().all())

        return CourseDetailMapper.to_course_detail(course_orm, place_orms)

    async def find_others_by_request_id(
        self, request_id: str, exclude_course_id: str
    ) -> list[SubCourse]:
        result = await self._session.execute(
            select(CourseOrm).where(
                CourseOrm.request_id == request_id,
                CourseOrm.course_id != exclude_course_id,
            )
        )
        return [CourseDetailMapper.to_sub_course(orm) for orm in result.scalars().all()]
