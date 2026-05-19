from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class RawContent(Base):
    __tablename__ = "raw_contents"

    RC_ID = Column(String(10), primary_key=True)
    category = Column(String(50), nullable=False)
    content_type = Column(String(20), nullable=False)  # memory/word/single_choice/multiple_choice
    raw_text = Column(Text, nullable=False)
    source = Column(String(20), default="excel_cell")
    process_status = Column(String(20), default="unprocessed")  # unprocessed/processing/processed/failed
    data_flag = Column(Integer, default=0)
    imported_at = Column(DateTime, default=datetime.utcnow)

    processed_contents = relationship("ProcessedContent", back_populates="raw_content")
