from dataclasses import dataclass
from typing import Optional


@dataclass
class SendEmailResponseDto:
    success: bool
    message: Optional[str] = None
