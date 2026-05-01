from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domains.courses.domain.exception import (
    InvalidEventNameException as CoursesInvalidEventNameException,
)
from app.domains.home.domain.exception import (
    InvalidEventNameException as HomeInvalidEventNameException,
)
from app.domains.recommendation.domain.exception import CourseNotFoundException


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        messages = [
            f"{'.'.join(str(loc) for loc in e['loc'] if loc != 'body')}: {e['msg']}"
            for e in exc.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": messages})

    @app.exception_handler(CoursesInvalidEventNameException)
    @app.exception_handler(HomeInvalidEventNameException)
    async def invalid_event_name_handler(
        request: Request,
        exc: CoursesInvalidEventNameException | HomeInvalidEventNameException,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(CourseNotFoundException)
    async def course_not_found_handler(request: Request, exc: CourseNotFoundException) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def general_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "서버 오류가 발생했습니다."})
