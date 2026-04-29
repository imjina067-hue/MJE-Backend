from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    event_name: str
    session_id: str
    created_at: datetime
    id: Optional[int] = None
