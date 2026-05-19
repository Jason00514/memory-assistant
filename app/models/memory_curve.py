from sqlalchemy import Column, String, Integer, JSON, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class MemoryCurve(Base):
    __tablename__ = "memory_curves"

    curve_id = Column(String(10), primary_key=True)
    curve_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    intervals = Column(JSON, nullable=False)          # [h1, h2, h3, h4, h5, h6, h7]
    overdue_multiplier = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_flag = Column(Integer, default=0)            # 0=normal, 1=deleted, 2=test

    processed_contents = relationship("ProcessedContent", back_populates="curve")
