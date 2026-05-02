from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmailPort(Protocol):
    async def send(self, to: str, subject: str, html_body: str) -> None: ...
