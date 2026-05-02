from dataclasses import dataclass


@dataclass(frozen=True)
class SendEmailRequestDto:
    email: str
    course_id: str
