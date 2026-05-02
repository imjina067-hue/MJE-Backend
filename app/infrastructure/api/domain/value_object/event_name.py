from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, FrozenSet

from app.infrastructure.api.domain.exception import InvalidEventNameException


@dataclass(frozen=True)
class EventName:
    ALLOWED: ClassVar[FrozenSet[str]] = frozenset({"course_export", "course_send", "export_close"})

    value: str

    def __post_init__(self) -> None:
        if self.value not in self.ALLOWED:
            raise InvalidEventNameException(self.value)
