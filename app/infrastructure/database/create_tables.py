import app.domains.home.repository.orm.home_event_orm  # noqa: F401
import app.domains.recommendation.repository.orm.recommendation_request_orm  # noqa: F401
import app.domains.courses.repository.orm.course_orm  # noqa: F401
import app.domains.courses.repository.orm.course_place_orm  # noqa: F401
import app.domains.courses.repository.orm.courses_event_orm  # noqa: F401
import app.infrastructure.api.repository.orm.email_log_orm  # noqa: F401

from app.infrastructure.database.base import Base
from app.infrastructure.database.session import _engine


async def create_tables() -> None:
    if _engine is None:
        return
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
