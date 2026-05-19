from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RawContentOut(BaseModel):
    RC_ID: str
    category: str
    content_type: str
    raw_text: str
    source: str
    process_status: str
    data_flag: int
    imported_at: datetime

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    total_imported: int
    failed: int
    items: list[RawContentOut]
