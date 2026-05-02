from dataclasses import dataclass


@dataclass(frozen=True)
class TrackExportEventRequestDto:
    event_name: str
    session_id: str
    page_path: str
