from dataclasses import dataclass
from typing import Optional


@dataclass
class TrackExportEventResponseDto:
    success: bool
    message: Optional[str] = None
