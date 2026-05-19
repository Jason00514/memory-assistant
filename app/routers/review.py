from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import processed_content as crud_pc
from app.crud import memory_curve as crud_curve
from app.schemas.processed_content import ReviewItem, ReviewAnswer, ReviewResult, ProcessedContentOut
from app.services.review_scheduler import process_review, get_review_type, _get_interval_hours

router = APIRouter(prefix="/review", tags=["review"])

DEFAULT_INTERVALS = [1, 4, 24, 48, 168, 360, 720]
DEFAULT_OVERDUE_MULTIPLIER = 10


def _get_intervals_and_multiplier(db: Session, curve_id: str | None) -> tuple[list[int], int]:
    if curve_id:
        curve = crud_curve.get_curve(db, curve_id)
        if curve:
            return curve.intervals, curve.overdue_multiplier
    return DEFAULT_INTERVALS, DEFAULT_OVERDUE_MULTIPLIER


def _to_review_item(pc, intervals: list[int], overdue_multiplier: int) -> ReviewItem:
    now = datetime.utcnow()
    if pc.next_review_time:
        hours_until = (pc.next_review_time - now).total_seconds() / 3600
        is_overdue = hours_until < 0
        review_type = get_review_type(now, pc.next_review_time, pc.current_level, intervals, overdue_multiplier)
        is_severely = review_type == "severely_overdue"
    else:
        hours_until = None
        is_overdue = False
        is_severely = False

    return ReviewItem(
        PC_ID=pc.PC_ID,
        content_type=pc.content_type,
        question=pc.question,
        answer=pc.answer,
        extra=pc.extra,
        category=pc.category,
        current_level=pc.current_level,
        next_review_time=pc.next_review_time,
        hours_until_review=round(hours_until, 1) if hours_until is not None else None,
        is_overdue=is_overdue,
        is_severely_overdue=is_severely,
    )


@router.get("/due", response_model=list[ReviewItem])
def get_due_items(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    records = crud_pc.get_due_for_review(db, category=category)
    result = []
    for pc in records:
        intervals, multiplier = _get_intervals_and_multiplier(db, pc.curve_id)
        result.append(_to_review_item(pc, intervals, multiplier))
    return result


@router.get("/all", response_model=list[ReviewItem])
def get_all_items(
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    records = crud_pc.get_all_active(db, category=category)
    result = []
    for pc in records:
        intervals, multiplier = _get_intervals_and_multiplier(db, pc.curve_id)
        result.append(_to_review_item(pc, intervals, multiplier))
    return result


@router.post("/answer", response_model=ReviewResult)
def submit_answer(body: ReviewAnswer, db: Session = Depends(get_db)):
    pc = crud_pc.get_by_id(db, body.PC_ID)
    if not pc:
        raise HTTPException(status_code=404, detail="Item not found")

    intervals, multiplier = _get_intervals_and_multiplier(db, pc.curve_id)
    now = datetime.utcnow()
    result = process_review(
        now=now,
        next_review_time=pc.next_review_time,
        current_level=pc.current_level,
        is_correct=body.is_correct,
        intervals=intervals,
        overdue_multiplier=multiplier,
    )

    crud_pc.update_review_result(
        db,
        pc,
        new_level=result["new_level"],
        last_reviewed_at=result["last_reviewed_at"],
        next_review_time=result["next_review_time"],
    )
    db.commit()

    return ReviewResult(
        PC_ID=body.PC_ID,
        old_level=result["old_level"],
        new_level=result["new_level"],
        next_review_time=result["next_review_time"],
        review_type=result["review_type"],
    )


@router.post("/reset/{pc_id}", response_model=ProcessedContentOut)
def reset_item(pc_id: str, level: int = Query(1, ge=1, le=7), db: Session = Depends(get_db)):
    pc = crud_pc.reset_level(db, pc_id, level)
    if not pc:
        raise HTTPException(status_code=404, detail="Item not found")
    return pc
