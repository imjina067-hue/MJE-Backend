from app.domains.tracking.domain.entity.event import Event
from app.domains.tracking.repository.orm.tracking_event_orm import TrackingEventOrm


class EventMapper:

    @staticmethod
    def to_orm(event: Event) -> TrackingEventOrm:
        return TrackingEventOrm(
            event_name=event.event_name,
            session_id=event.session_id,
            created_at=event.created_at,
        )

    @staticmethod
    def to_entity(orm: TrackingEventOrm) -> Event:
        return Event(
            id=orm.id,
            event_name=orm.event_name,
            session_id=orm.session_id,
            created_at=orm.created_at,
        )
