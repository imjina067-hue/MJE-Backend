from fastapi import APIRouter, Depends

from app.domains.recommendation.controller.api.request_form.create_course_request_form import (
    CreateCourseRequestForm,
)
from app.domains.recommendation.controller.api.response_form.create_course_response_form import (
    CreateCourseResponseForm,
)
from app.domains.recommendation.service.usecase.create_course_usecase import CreateCourseUseCase
from app.infrastructure.dependencies import get_create_course_usecase

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/create-course", response_model=CreateCourseResponseForm)
async def create_course(
    form: CreateCourseRequestForm,
    usecase: CreateCourseUseCase = Depends(get_create_course_usecase),
) -> CreateCourseResponseForm:
    dto = form.to_request()
    result = await usecase.execute(dto)
    return CreateCourseResponseForm.from_response(result)
