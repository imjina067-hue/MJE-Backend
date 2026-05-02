from fastapi import APIRouter, Depends

from app.infrastructure.api.controller.api.request_form.send_email_request_form import SendEmailRequestForm
from app.infrastructure.api.controller.api.response_form.send_email_response_form import SendEmailResponseForm
from app.infrastructure.api.service.usecase.send_email_usecase import SendEmailUseCase
from app.infrastructure.dependencies import get_send_email_usecase

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/email", response_model=SendEmailResponseForm)
async def send_email(
    form: SendEmailRequestForm,
    usecase: SendEmailUseCase = Depends(get_send_email_usecase),
) -> SendEmailResponseForm:
    dto = form.to_request()
    result = await usecase.execute(dto)
    return SendEmailResponseForm.from_response(result)
