from fastapi import APIRouter, Depends

from app.domains.home.controller.api.request_form.track_event_request_form import TrackEventRequestForm
from app.domains.home.controller.api.response_form.track_event_response_form import TrackEventResponseForm
from app.domains.home.domain.exception import InvalidEventNameException
from app.domains.home.service.usecase.track_event_usecase import TrackEventUseCase
from app.infrastructure.dependencies import get_home_track_event_usecase

router = APIRouter(prefix="/home", tags=["home"])


@router.post("/events", response_model=TrackEventResponseForm)
async def track_event(
    form: TrackEventRequestForm,
    usecase: TrackEventUseCase = Depends(get_home_track_event_usecase),
) -> TrackEventResponseForm:
    dto = form.to_request()
    result = await usecase.execute(dto)
    return TrackEventResponseForm.from_response(result)
