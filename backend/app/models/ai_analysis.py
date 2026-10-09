"""AI 分析记录（预留）。"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey

from app.core.db import Base


class AIAnalysis(Base):
    """AI分析记录（预留）"""
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("trigger_events.id"), nullable=True)
    ai_model = Column(String(100))
    analysis_result = Column(Text)                    # JSON 格式结果
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
