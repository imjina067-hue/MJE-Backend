from fastapi import APIRouter, Depends

from app.infrastructure.api.controller.api.request_form.track_export_event_request_form import TrackExportEventRequestForm
from app.infrastructure.api.controller.api.response_form.track_export_event_response_form import TrackExportEventResponseForm
from app.infrastructure.api.service.usecase.track_export_event_usecase import TrackExportEventUseCase
from app.infrastructure.dependencies import get_export_track_event_usecase

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/send-events", response_model=TrackExportEventResponseForm)
async def track_send_event(
    form: TrackExportEventRequestForm,
    usecase: TrackExportEventUseCase = Depends(get_export_track_event_usecase),
) -> TrackExportEventResponseForm:
    dto = form.to_request()
    result = await usecase.execute(dto)
    return TrackExportEventResponseForm.from_response(result)
