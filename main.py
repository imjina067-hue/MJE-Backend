import uvicorn
from fastapi import FastAPI

from app.domains.recommendation.controller.api.recommendation_router import router as recommendation_router
from app.domains.tracking.controller.api.tracking_router import router as tracking_router
from app.infrastructure.config import get_settings
from app.infrastructure.exception_handler import register_exception_handlers

app = FastAPI(title="Pioneer Team Backend")

get_settings()

register_exception_handlers(app)

app.include_router(recommendation_router)
app.include_router(tracking_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=33333, reload=True)
