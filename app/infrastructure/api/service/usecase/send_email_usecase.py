from __future__ import annotations

from app.domains.recommendation.domain.exception import CourseNotFoundException
from app.domains.recommendation.repository.course_detail_repository import CourseDetailRepository
from app.infrastructure.api.service.dto.request.send_email_request_dto import SendEmailRequestDto
from app.infrastructure.api.service.dto.response.send_email_response_dto import SendEmailResponseDto
from app.infrastructure.config.settings import get_settings
from app.infrastructure.external.email_port import EmailPort


def _build_html(course) -> str:  # type: ignore[no-untyped-def]
    places_rows = "".join(
        f"<tr>"
        f"<td style='padding:8px;border:1px solid #ddd;'>{p.visit_order}</td>"
        f"<td style='padding:8px;border:1px solid #ddd;'>{p.name}</td>"
        f"<td style='padding:8px;border:1px solid #ddd;'>{p.category}</td>"
        f"<td style='padding:8px;border:1px solid #ddd;'>{p.duration_minutes}분</td>"
        f"</tr>"
        for p in course.places
    )
    return f"""
<html>
<body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <h2 style="color:#333;">{course.title}</h2>
  <p style="color:#555;">{course.description}</p>
  <table style="width:100%;border-collapse:collapse;margin-top:12px;">
    <tr style="background:#f5f5f5;">
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">순서</th>
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">장소</th>
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">카테고리</th>
      <th style="padding:8px;border:1px solid #ddd;text-align:left;">소요 시간</th>
    </tr>
    {places_rows}
  </table>
  <p style="margin-top:16px;color:#777;">
    📍 {course.location_summary} &nbsp;|&nbsp; 🕐 총 {course.total_duration}분 &nbsp;|&nbsp; 🗺️ {course.route_summary}
  </p>
</body>
</html>
"""


class SendEmailUseCase:

    def __init__(
        self,
        course_repository: CourseDetailRepository,
        email_port: EmailPort,
    ) -> None:
        self._course_repository = course_repository
        self._email_port = email_port

    async def execute(self, dto: SendEmailRequestDto) -> SendEmailResponseDto:
        course = await self._course_repository.find_by_course_id(dto.course_id)
        if course is None:
            raise CourseNotFoundException(dto.course_id)

        service_name = get_settings().SERVICE_NAME
        subject = f"[{service_name}] {course.title}"
        html_body = _build_html(course)

        try:
            await self._email_port.send(to=dto.email, subject=subject, html_body=html_body)
            return SendEmailResponseDto(success=True)
        except Exception as e:
            return SendEmailResponseDto(success=False, message=str(e))
