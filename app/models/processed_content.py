from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcessedContent(Base):
    __tablename__ = "processed_contents"

    PC_ID = Column(String(10), primary_key=True)
    RC_ID = Column(String(10), ForeignKey("raw_contents.RC_ID"), nullable=False)
    content_type = Column(String(20), nullable=False)   # word/memory/single_choice/multiple_choice
    question = Column(Text, nullable=False)
    answer = Column(Text, default="NONE")
    extra = Column(JSON, nullable=True)                 # options, correct_answers, explanation
    category = Column(String(50), nullable=False)
    usage_type = Column(String(30), nullable=True)      # english_word/exam_practice/daily_review
    curve_id = Column(String(10), ForeignKey("memory_curves.curve_id"), nullable=True)
    current_level = Column(Integer, default=1)          # 1-7
    last_reviewed_at = Column(DateTime, nullable=True)
    next_review_time = Column(DateTime, nullable=True)
    process_version = Column(Integer, default=1)
    data_flag = Column(Integer, default=0)
    processed_at = Column(DateTime, default=datetime.utcnow)

    raw_content = relationship("RawContent", back_populates="processed_contents")
    curve = relationship("MemoryCurve", back_populates="processed_contents")
