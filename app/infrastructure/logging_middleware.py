import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Request 출력
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes) if body_bytes else None
        except Exception:
            body = body_bytes.decode("utf-8", errors="replace") if body_bytes else None

        print("\n========== REQUEST ==========")
        print(f"Method  : {request.method}")
        print(f"URL     : {request.url}")
        print(f"Headers : {dict(request.headers)}")
        print(f"Body    : {body}")
        print("==============================\n")

        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start

        # Response body 읽기
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        try:
            response_json = json.loads(response_body)
        except Exception:
            response_json = response_body.decode("utf-8", errors="replace")

        print("\n========== RESPONSE ==========")
        print(f"Status  : {response.status_code}")
        print(f"Time    : {elapsed:.3f}s")
        print(f"Body    : {response_json}")
        print("==============================\n")

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
