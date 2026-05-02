import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.courses.controller.api.courses_router import router as courses_router
from app.infrastructure.api.controller.api.export_router import router as export_router
from app.infrastructure.api.controller.api.email_router import router as email_router
from app.infrastructure.api.controller.api.send_event_router import router as send_event_router
from app.infrastructure.api.controller.api.close_event_router import router as close_event_router
from app.domains.home.controller.api.home_router import router as home_router
from app.domains.recommendation.controller.api.recommendation_router import router as recommendation_router
from app.infrastructure.config import get_settings
from app.infrastructure.database.create_tables import create_tables
from app.infrastructure.exception_handler import register_exception_handlers
from app.infrastructure.logging_middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title="Pioneer Team Backend", lifespan=lifespan)

settings = get_settings()

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(home_router)
app.include_router(courses_router)
app.include_router(export_router)
app.include_router(email_router)
app.include_router(send_event_router)
app.include_router(close_event_router)
app.include_router(recommendation_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=33333, reload=True)
