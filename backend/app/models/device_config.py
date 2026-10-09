"""设备配置（键值对）。"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.core.db import Base


class DeviceConfig(Base):
    """设备配置"""
    __tablename__ = "device_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
