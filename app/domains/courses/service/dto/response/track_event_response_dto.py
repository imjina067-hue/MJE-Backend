from dataclasses import dataclass
from typing import Optional


@dataclass
class TrackEventResponseDto:
    success: bool
    message: Optional[str] = None
