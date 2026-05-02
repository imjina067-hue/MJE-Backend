from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domains.recommendation.controller.api.response_form.suggested_course_response_forms import (
    ActivitiesResponseForm,
    CafesResponseForm,
    ExplainTextResponseForm,
    HashtagResponseForm,
    ImageResponseForm,
    LocationResponseForm,
    OtherCoursesResponseForm,
    RestaurantsResponseForm,
)
from app.domains.recommendation.service.usecase.get_suggested_course_usecase import GetSuggestedCourseUseCase
from app.infrastructure.dependencies import get_suggested_course_usecase

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


@router.get(
    "/suggested-courses/{course_id}/explain-text",
    response_model=ExplainTextResponseForm,
)
async def get_explain_text(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> ExplainTextResponseForm:
    return ExplainTextResponseForm.from_response(usecase.get_explain_text(course_id))


@router.get(
    "/suggested-courses/{course_id}/hashtag",
    response_model=HashtagResponseForm,
)
async def get_hashtag(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> HashtagResponseForm:
    return HashtagResponseForm.from_response(usecase.get_hashtag(course_id))


@router.get(
    "/suggested-courses/{course_id}/location",
    response_model=LocationResponseForm,
)
async def get_location(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> LocationResponseForm:
    return LocationResponseForm.from_response(usecase.get_location(course_id))


@router.get(
    "/suggested-courses/{course_id}/image",
    response_model=ImageResponseForm,
)
async def get_image(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> ImageResponseForm:
    return ImageResponseForm.from_response(usecase.get_image(course_id))


@router.get(
    "/detail/{course_id}/restaurants",
    response_model=RestaurantsResponseForm,
)
async def get_restaurants(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> RestaurantsResponseForm:
    return RestaurantsResponseForm.from_response(usecase.get_restaurants(course_id))


@router.get(
    "/detail/{course_id}/cafes",
    response_model=CafesResponseForm,
)
async def get_cafes(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> CafesResponseForm:
    return CafesResponseForm.from_response(usecase.get_cafes(course_id))


@router.get(
    "/detail/{course_id}/activities",
    response_model=ActivitiesResponseForm,
)
async def get_activities(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> ActivitiesResponseForm:
    return ActivitiesResponseForm.from_response(usecase.get_activities(course_id))


@router.get(
    "/detail/{course_id}/other-courses",
    response_model=OtherCoursesResponseForm,
)
async def get_other_courses(
    course_id: str,
    usecase: GetSuggestedCourseUseCase = Depends(get_suggested_course_usecase),
) -> OtherCoursesResponseForm:
    return OtherCoursesResponseForm.from_response(usecase.get_other_courses(course_id))
