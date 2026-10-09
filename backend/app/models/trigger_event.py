"""触发事件记录。"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float

from app.core.db import Base


class TriggerEvent(Base):
    """触发事件记录"""
    __tablename__ = "trigger_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_time = Column(DateTime, nullable=False, index=True)   # 触发时间
    sensor_id = Column(String(10), nullable=False, index=True)  # 传感器编号
    audio_file = Column(String(255))                             # 播放的音频文件
    temperature = Column(Float)                                 # 触发时温度
    humidity = Column(Float)                                    # 触发时湿度
    battery_voltage = Column(Float)                             # 触发时电池电压
    synced_at = Column(DateTime, default=datetime.utcnow)       # 同步到后台的时间
