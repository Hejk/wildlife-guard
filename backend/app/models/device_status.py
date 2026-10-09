"""设备状态快照。"""
from sqlalchemy import Column, Integer, DateTime, Float

from app.core.db import Base


class DeviceStatus(Base):
    """设备状态快照"""
    __tablename__ = "device_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reported_at = Column(DateTime, nullable=False, index=True)
    battery_voltage = Column(Float)
    sd_card_total_mb = Column(Integer)
    sd_card_used_mb = Column(Integer)
    uptime_seconds = Column(Integer)
    temperature = Column(Float)
    humidity = Column(Float)
