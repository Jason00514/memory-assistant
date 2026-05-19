"""
記憶カーブルーター：CRUD + プレビュー機能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import memory_curve as crud
from app.schemas.memory_curve import (
    MemoryCurveCreate, MemoryCurveUpdate, MemoryCurveOut,
    CurvePreview, CurvePreviewEntry,
)

router = APIRouter(prefix="/curves", tags=["memory-curves"])


def _format_hours(h: float) -> str:
    """時間数を人間が読みやすい文字列に変換する"""
    if h < 1:
        return f"{int(h * 60)}分後"
    if h < 24:
        return f"{h:.0f}時間後"
    if h < 24 * 7:
        return f"{h / 24:.1f}日後"
    return f"{h / 24 / 7:.1f}週間後"


@router.get("/", response_model=list[MemoryCurveOut])
def list_curves(db: Session = Depends(get_db)):
    return crud.list_curves(db)


@router.post("/", response_model=MemoryCurveOut)
def create_curve(data: MemoryCurveCreate, db: Session = Depends(get_db)):
    return crud.create_curve(db, data)


@router.get("/{curve_id}", response_model=MemoryCurveOut)
def get_curve(curve_id: str, db: Session = Depends(get_db)):
    curve = crud.get_curve(db, curve_id)
    if not curve:
        raise HTTPException(status_code=404, detail="Curve not found")
    return curve


@router.get("/{curve_id}/preview", response_model=CurvePreview)
def preview_curve(curve_id: str, db: Session = Depends(get_db)):
    """
    カーブを選択したとき、全て正解した場合の復習スケジュールをプレビューする。
    例：Level1 → 1時間後、Level2 → 5時間後（累計）、...
    """
    curve = crud.get_curve(db, curve_id)
    if not curve:
        raise HTTPException(status_code=404, detail="Curve not found")

    schedule = []
    cumulative_hours = 0.0
    for i, interval in enumerate(curve.intervals):
        cumulative_hours += interval
        schedule.append(CurvePreviewEntry(
            level=i + 1,
            hours_from_start=cumulative_hours,
            review_date_label=_format_hours(cumulative_hours),
        ))

    return CurvePreview(
        curve_id=curve.curve_id,
        curve_name=curve.curve_name,
        schedule=schedule,
        total_days=round(cumulative_hours / 24, 1),
        total_reviews=7,  # 全て正解した場合の最小復習回数
    )


@router.put("/{curve_id}", response_model=MemoryCurveOut)
def update_curve(curve_id: str, data: MemoryCurveUpdate, db: Session = Depends(get_db)):
    curve = crud.update_curve(db, curve_id, data)
    if not curve:
        raise HTTPException(status_code=404, detail="Curve not found")
    return curve


@router.delete("/{curve_id}")
def delete_curve(curve_id: str, db: Session = Depends(get_db)):
    if not crud.delete_curve(db, curve_id):
        raise HTTPException(status_code=404, detail="Curve not found")
    return {"message": "Deleted"}
