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
    PC_ID: str
    content_type: str
    question: str
    answer: str
    extra: Optional[Any] = None
    category: str
    current_level: int
    next_review_time: Optional[datetime] = None
    hours_until_review: Optional[float] = None
    is_overdue: bool = False
    is_severely_overdue: bool = False

    model_config = {"from_attributes": True}


class ReviewAnswer(BaseModel):
    PC_ID: str
    is_correct: bool


class ReviewResult(BaseModel):
    PC_ID: str
    old_level: int
    new_level: int
    next_review_time: datetime
    review_type: str  # normal/early/severely_overdue


class ProcessRequest(BaseModel):
    rc_ids: Optional[list[str]] = None  # None = process all unprocessed
    curve_id: Optional[str] = None      # None = use default curve


class ProcessResult(BaseModel):
    total_processed: int
    failed: int
    items: list[ProcessedContentOut]
