"""音频文件管理。"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, DateTime

from app.core.db import Base


class AudioFile(Base):
    """音频文件管理"""
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False, unique=True)
    category = Column(String(50), default="通用驱赶")           # 分类
    duration_seconds = Column(Integer)                          # 时长
    file_size = Column(BigInteger)                             # 文件大小(字节)
    status = Column(String(20), default="local")               # local/synced/deleted
    uploaded_at = Column(DateTime, default=datetime.utcnow)    # 上传/同步到设备的时间
