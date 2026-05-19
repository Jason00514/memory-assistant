"""
ProcessedContent 関連の Pydantic スキーマ（APIリクエスト/レスポンス形式）
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class ProcessedContentOut(BaseModel):
    PC_ID: str
    RC_ID: str
    content_type: str
    question: str
    answer: str
    extra: Optional[Any] = None
    category: str
    tags: Optional[list[str]] = None          # 追加タグ一覧
    usage_type: Optional[str] = None
    curve_id: Optional[str] = None
    current_level: int
    last_reviewed_at: Optional[datetime] = None
    next_review_time: Optional[datetime] = None
    process_version: int
    data_flag: int
    processed_at: datetime

    model_config = {"from_attributes": True}


class ReviewItem(BaseModel):
    """復習画面で1枚分のカードデータ"""
    PC_ID: str
    content_type: str
    question: str
    answer: str
    extra: Optional[Any] = None
    category: str
    tags: Optional[list[str]] = None
    current_level: int
    next_review_time: Optional[datetime] = None
    hours_until_review: Optional[float] = None   # 正=まだ時間あり、負=過期
    is_overdue: bool = False
    is_severely_overdue: bool = False

    model_config = {"from_attributes": True}


class ReviewAnswer(BaseModel):
    """答え合わせ送信データ"""
    PC_ID: str
    is_correct: bool


class ReviewResult(BaseModel):
    """答え合わせ後に返す結果"""
    PC_ID: str
    old_level: int
    new_level: int
    next_review_time: datetime
    review_type: str     # normal / early / severely_overdue


class ProcessRequest(BaseModel):
    """RawContent → ProcessedContent 変換リクエスト"""
    rc_ids: Optional[list[str]] = None    # 指定なし = 全未処理
    curve_id: Optional[str] = None        # 指定なし = デフォルトカーブ


class ProcessResult(BaseModel):
    total_processed: int
    failed: int
    items: list[ProcessedContentOut]


class UpdateTagsRequest(BaseModel):
    """カードのタグを更新するリクエスト"""
    tags: list[str]


class UpdateCurveRequest(BaseModel):
    """カードの記憶カーブを変更するリクエスト"""
    curve_id: str
