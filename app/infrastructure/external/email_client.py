from __future__ import annotations

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.infrastructure.config.settings import get_settings


class EmailClient:

    def __init__(self) -> None:
        s = get_settings()
        self._host = s.SMTP_HOST
        self._port = s.SMTP_PORT
        self._user = s.SMTP_USER
        self._password = s.SMTP_PASSWORD
        self._from = s.SMTP_FROM

    def _is_configured(self) -> bool:
        return all([self._host, self._user, self._password, self._from])

    def _send_sync(self, to: str, subject: str, html_body: str) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self._from
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(self._host, self._port) as server:
            server.ehlo()
            server.starttls()
            server.login(self._user, self._password)
            server.sendmail(self._from, to, msg.as_string())

    async def send(self, to: str, subject: str, html_body: str) -> None:
        if not self._is_configured():
            raise RuntimeError("SMTP 설정이 되어 있지 않습니다. SMTP_* 환경 변수를 확인해주세요.")
        await asyncio.to_thread(self._send_sync, to, subject, html_body)
