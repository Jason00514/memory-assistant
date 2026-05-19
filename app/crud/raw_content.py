from datetime import datetime
from sqlalchemy.orm import Session
from app.models.raw_content import RawContent
from app.utils.id_generator import generate_rc_id


def create_raw_content(db: Session, category: str, content_type: str, raw_text: str) -> RawContent:
    rc_id = generate_rc_id(db)
    record = RawContent(
        RC_ID=rc_id,
        category=category,
        content_type=content_type,
        raw_text=raw_text,
        source="excel_cell",
        process_status="unprocessed",
        data_flag=0,
        imported_at=datetime.utcnow(),
    )
    db.add(record)
    return record


def get_unprocessed(db: Session) -> list[RawContent]:
    return db.query(RawContent).filter(
        RawContent.process_status == "unprocessed",
        RawContent.data_flag == 0,
    ).all()


def get_by_ids(db: Session, rc_ids: list[str]) -> list[RawContent]:
    return db.query(RawContent).filter(
        RawContent.RC_ID.in_(rc_ids),
        RawContent.data_flag == 0,
    ).all()


def set_process_status(db: Session, record: RawContent, status: str) -> None:
    record.process_status = status


def list_raw_contents(db: Session, category: str | None = None) -> list[RawContent]:
    q = db.query(RawContent).filter(RawContent.data_flag == 0)
    if category:
        q = q.filter(RawContent.category == category)
    return q.order_by(RawContent.imported_at.desc()).all()
