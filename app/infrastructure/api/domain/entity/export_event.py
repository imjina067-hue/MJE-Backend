from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExportEvent:
    event_name: str
    session_id: str
    page_path: str
    created_at: datetime
    id: Optional[int] = None
