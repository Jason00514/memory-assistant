"""
ProcessedContent テーブル定義
RawContent を解析して生成した「復習カード」を管理するテーブル。
1枚の RawContent から 1枚の ProcessedContent が生成される。
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcessedContent(Base):
    __tablename__ = "processed_contents"

    PC_ID = Column(String(10), primary_key=True)           # 例: PC_0000001
    RC_ID = Column(String(10), ForeignKey("raw_contents.RC_ID"), nullable=False)

    content_type = Column(String(20), nullable=False)       # word/memory/single_choice/multiple_choice
    question = Column(Text, nullable=False)                 # 表面に表示する問題文
    answer = Column(Text, default="NONE")                   # 答え（なければ "NONE"）
    extra = Column(JSON, nullable=True)                     # 選択肢・解説など付加情報 {options, correct_answers, explanation}

    category = Column(String(50), nullable=False)           # 主カテゴリ（インポート時に設定）
    tags = Column(JSON, nullable=True, default=list)        # 追加タグ一覧 例: ["英語四級", "AI語彙"]

    usage_type = Column(String(30), nullable=True)          # english_word / exam_practice / daily_review
    curve_id = Column(String(10), ForeignKey("memory_curves.curve_id"), nullable=True)

    current_level = Column(Integer, default=1)              # 現在の記憶レベル 1-7
    last_reviewed_at = Column(DateTime, nullable=True)      # 最後に復習した日時
    next_review_time = Column(DateTime, nullable=True)      # 次回復習予定日時（null = 未復習）

    process_version = Column(Integer, default=1)            # 解析バージョン（再解析時に増加）
    data_flag = Column(Integer, default=0)                  # 0=正常, 1=削除済, 2=テスト
    processed_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    raw_content = relationship("RawContent", back_populates="processed_contents")
    curve = relationship("MemoryCurve", back_populates="processed_contents")
