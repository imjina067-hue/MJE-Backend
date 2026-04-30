from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, FrozenSet

from app.domains.home.domain.exception import InvalidEventNameException


@dataclass(frozen=True)
class EventName:
    ALLOWED: ClassVar[FrozenSet[str]] = frozenset({"logo_click"})

    value: str

    def __post_init__(self) -> None:
        if self.value not in self.ALLOWED:
            raise InvalidEventNameException(self.value)
