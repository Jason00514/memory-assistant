from datetime import datetime
from sqlalchemy.orm import Session
from app.models.processed_content import ProcessedContent
from app.utils.id_generator import generate_pc_id


def create_processed_content(
    db: Session,
    rc_id: str,
    content_type: str,
    question: str,
    answer: str,
    extra,
    category: str,
    usage_type: str | None,
    curve_id: str | None,
) -> ProcessedContent:
    pc_id = generate_pc_id(db)
    record = ProcessedContent(
        PC_ID=pc_id,
        RC_ID=rc_id,
        content_type=content_type,
        question=question,
        answer=answer,
        extra=extra,
        category=category,
        usage_type=usage_type,
        curve_id=curve_id,
        current_level=1,
        last_reviewed_at=None,
        next_review_time=None,
        process_version=1,
        data_flag=0,
        processed_at=datetime.utcnow(),
    )
    db.add(record)
    return record


def get_due_for_review(db: Session, category: str | None = None) -> list[ProcessedContent]:
    now = datetime.utcnow()
    q = db.query(ProcessedContent).filter(
        ProcessedContent.data_flag == 0,
        (ProcessedContent.next_review_time == None) | (ProcessedContent.next_review_time <= now),
    )
    if category:
        q = q.filter(ProcessedContent.category == category)
    return q.order_by(ProcessedContent.next_review_time.asc().nullsfirst()).all()


def get_all_active(db: Session, category: str | None = None) -> list[ProcessedContent]:
    q = db.query(ProcessedContent).filter(ProcessedContent.data_flag == 0)
    if category:
        q = q.filter(ProcessedContent.category == category)
    return q.order_by(ProcessedContent.next_review_time.asc().nullsfirst()).all()


def get_by_id(db: Session, pc_id: str) -> ProcessedContent | None:
    return db.query(ProcessedContent).filter(
        ProcessedContent.PC_ID == pc_id,
        ProcessedContent.data_flag == 0,
    ).first()


def update_review_result(
    db: Session,
    record: ProcessedContent,
    new_level: int,
    last_reviewed_at: datetime,
    next_review_time: datetime,
) -> None:
    record.current_level = new_level
    record.last_reviewed_at = last_reviewed_at
    record.next_review_time = next_review_time


def reset_level(db: Session, pc_id: str, level: int = 1) -> ProcessedContent | None:
    record = get_by_id(db, pc_id)
    if not record:
        return None
    record.current_level = max(1, min(7, level))
    record.next_review_time = None
    record.last_reviewed_at = None
    db.commit()
    db.refresh(record)
    return record
