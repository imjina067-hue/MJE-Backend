from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrackEventResponseDto:
    event_name: str
    session_id: str
    timestamp: datetime
    page_path: str
