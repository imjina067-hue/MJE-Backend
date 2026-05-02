from app.infrastructure.api.domain.entity.export_event import ExportEvent
from app.infrastructure.api.repository.orm.export_log_orm import ExportLogOrm


class ExportLogMapper:

    @staticmethod
    def to_orm(event: ExportEvent) -> ExportLogOrm:
        return ExportLogOrm(
            event_name=event.event_name,
            session_id=event.session_id,
            page_path=event.page_path,
            created_at=event.created_at,
        )

    @staticmethod
    def to_entity(orm: ExportLogOrm) -> ExportEvent:
        return ExportEvent(
            id=orm.id,
            event_name=orm.event_name,
            session_id=orm.session_id,
            page_path=orm.page_path,
            created_at=orm.created_at,
        )
