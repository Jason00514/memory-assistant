"""
MemoryCurve 関連の Pydantic スキーマ
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MemoryCurveBase(BaseModel):
    curve_name: str
    description: Optional[str] = None
    intervals: list[int] = Field(..., min_length=7, max_length=7)   # Level1-7 の間隔（時間単位）
    overdue_multiplier: int = 10                                     # 深刻過期の判定倍率


class MemoryCurveCreate(MemoryCurveBase):
    pass


class MemoryCurveUpdate(BaseModel):
    curve_name: Optional[str] = None
    description: Optional[str] = None
    intervals: Optional[list[int]] = None
    overdue_multiplier: Optional[int] = None


class MemoryCurveOut(MemoryCurveBase):
    curve_id: str
    created_at: datetime
    data_flag: int

    model_config = {"from_attributes": True}


class CurvePreviewEntry(BaseModel):
    """カーブプレビューの1行分（各Levelの復習予定日時）"""
    level: int
    hours_from_start: float      # スタートからの累計時間
    review_date_label: str       # 例: "4時間後" / "3日後"


class CurvePreview(BaseModel):
    """カーブ全体のプレビュー情報"""
    curve_id: str
    curve_name: str
    schedule: list[CurvePreviewEntry]   # Level1〜7 の復習スケジュール
    total_days: float                    # 全レベルクリアまでの日数
    total_reviews: int                   # 全て正解した場合の最小復習回数（=7）
