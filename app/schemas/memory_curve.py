from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class MemoryCurveBase(BaseModel):
    curve_name: str
    description: Optional[str] = None
    intervals: List[int] = Field(..., min_length=7, max_length=7)
    overdue_multiplier: int = 10


class MemoryCurveCreate(MemoryCurveBase):
    pass


class MemoryCurveUpdate(BaseModel):
    curve_name: Optional[str] = None
    description: Optional[str] = None
    intervals: Optional[List[int]] = None
    overdue_multiplier: Optional[int] = None


class MemoryCurveOut(MemoryCurveBase):
    curve_id: str
    created_at: datetime
    data_flag: int

    model_config = {"from_attributes": True}
