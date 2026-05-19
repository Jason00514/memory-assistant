"""
復習ルーター：今日の復習・答え合わせ・レベルリセット
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import processed_content as crud_pc
from app.crud import memory_curve as crud_curve
from app.schemas.processed_content import ReviewItem, ReviewAnswer, ReviewResult, ProcessedContentOut
from app.services.review_scheduler import process_review, get_review_type

router = APIRouter(prefix="/review", tags=["review"])

# カーブが設定されていないカードに使うフォールバック値
DEFAULT_INTERVALS = [1, 4, 24, 48, 168, 360, 720]   # Level1-7 の間隔（時間）
DEFAULT_OVERDUE_MULTIPLIER = 10


def _get_intervals_and_multiplier(db: Session, curve_id: str | None) -> tuple[list[int], int]:
    """カーブIDからインターバル配列と過期倍率を取得する。未設定時はデフォルト値を返す"""
    if curve_id:
        curve = crud_curve.get_curve(db, curve_id)
        if curve:
            return curve.intervals, curve.overdue_multiplier
    return DEFAULT_INTERVALS, DEFAULT_OVERDUE_MULTIPLIER


def _to_review_item(pc, intervals: list[int], overdue_multiplier: int) -> ReviewItem:
    """ProcessedContent モデルを ReviewItem スキーマに変換する"""
    now = datetime.utcnow()
    if pc.next_review_time:
        hours_until = (pc.next_review_time - now).total_seconds() / 3600
        is_overdue = hours_until < 0
        review_type = get_review_type(now, pc.next_review_time, pc.current_level, intervals, overdue_multiplier)
        is_severely = review_type == "severely_overdue"
    else:
        # 未復習カードは即時復習対象
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
        tags=pc.tags or [],
        current_level=pc.current_level,
        next_review_time=pc.next_review_time,
        hours_until_review=round(hours_until, 1) if hours_until is not None else None,
        is_overdue=is_overdue,
        is_severely_overdue=is_severely,
    )


@router.get("/due", response_model=list[ReviewItem])
def get_due_items(
    category: str | None = Query(None, description="カテゴリで絞り込む"),
    tag: str | None = Query(None, description="タグで絞り込む"),
    db: Session = Depends(get_db),
):
    """
    今日復習すべきカードを返す。
    過期が大きい順（最優先）に並べて返す。
    """
    records = crud_pc.get_due_for_review(db, category=category, tag=tag, sort_urgency=True)
    result = []
    for pc in records:
        intervals, multiplier = _get_intervals_and_multiplier(db, pc.curve_id)
        result.append(_to_review_item(pc, intervals, multiplier))
    return result


@router.get("/all", response_model=list[ReviewItem])
def get_all_items(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    status: str | None = Query(None, description="due / overdue / None(全て)"),
    db: Session = Depends(get_db),
):
    """全カード一覧を返す（カード库画面用）"""
    records = crud_pc.get_all_active(db, category=category, tag=tag, status_filter=status)
    result = []
    for pc in records:
        intervals, multiplier = _get_intervals_and_multiplier(db, pc.curve_id)
        result.append(_to_review_item(pc, intervals, multiplier))
    return result


@router.post("/answer", response_model=ReviewResult)
def submit_answer(body: ReviewAnswer, db: Session = Depends(get_db)):
    """
    答え合わせ結果を受け取り、レベルを更新して次回復習日時を計算する。
    """
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
        db, pc,
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
def reset_item(
    pc_id: str,
    level: int = Query(1, ge=1, le=7, description="リセット先のレベル"),
    db: Session = Depends(get_db),
):
    """指定カードのレベルをリセットし、次回復習日時をクリアする"""
    pc = crud_pc.reset_level(db, pc_id, level)
    if not pc:
        raise HTTPException(status_code=404, detail="Item not found")
    return pc
