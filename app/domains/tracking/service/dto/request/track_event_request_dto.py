from dataclasses import dataclass


@dataclass(frozen=True)
class TrackEventRequestDto:
    event_name: str
    session_id: str
