"""
Dashboard ルーター：カテゴリ別・全体統計を返す API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.processed_content import get_category_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)) -> list[dict]:
    """
    カテゴリ別の統計を返す。
    戻り値例：
    [
      {"category": "英語単語", "total": 100, "due": 30, "overdue": 10, "mastered": 5},
      ...
    ]
    """
    return get_category_stats(db)
