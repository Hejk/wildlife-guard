"""实体 Pydantic 模型（与 SQLAlchemy 模型对应）。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TriggerEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_time: datetime
    sensor_id: str
    audio_file: str | None = None
    temperature: float | None = None
    humidity: float | None = None
    battery_voltage: float | None = None
    synced_at: datetime | None = None


class TriggerEventCreate(BaseModel):
    """ESP32 上报的单条事件（sync_logs 解析用）。"""
    event_time: datetime
    sensor_id: str
    audio_file: str | None = None
    temperature: float | None = None
    humidity: float | None = None
    battery_voltage: float | None = None


class AudioFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    category: str | None = None
    duration_seconds: int | None = None
    file_size: int | None = None
    status: str
    uploaded_at: datetime | None = None


class DeviceConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    config_key: str
    config_value: str | None = None
    updated_at: datetime | None = None


class DeviceStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reported_at: datetime
    battery_voltage: float | None = None
    sd_card_total_mb: int | None = None
    sd_card_used_mb: int | None = None
    uptime_seconds: int | None = None
    temperature: float | None = None
    humidity: float | None = None
