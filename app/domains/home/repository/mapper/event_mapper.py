from app.domains.home.domain.entity.event import Event
from app.domains.home.repository.orm.home_event_orm import HomeEventOrm


class EventMapper:

    @staticmethod
    def to_orm(event: Event) -> HomeEventOrm:
        return HomeEventOrm(
            event_name=event.event_name,
            session_id=event.session_id,
            page_path=event.page_path,
            created_at=event.created_at,
        )

    @staticmethod
    def to_entity(orm: HomeEventOrm) -> Event:
        return Event(
            id=orm.id,
            event_name=orm.event_name,
            session_id=orm.session_id,
            page_path=orm.page_path,
            created_at=orm.created_at,
        )
