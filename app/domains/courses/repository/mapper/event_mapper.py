from app.domains.courses.domain.entity.event import Event
from app.domains.courses.repository.orm.courses_event_orm import CoursesEventOrm


class EventMapper:

    @staticmethod
    def to_orm(event: Event) -> CoursesEventOrm:
        return CoursesEventOrm(
            event_name=event.event_name,
            session_id=event.session_id,
            created_at=event.created_at,
        )

    @staticmethod
    def to_entity(orm: CoursesEventOrm) -> Event:
        return Event(
            id=orm.id,
            event_name=orm.event_name,
            session_id=orm.session_id,
            created_at=orm.created_at,
        )
