"""设备状态 / 串口 / 同步相关 schema。"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConnectRequest(BaseModel):
    port: str = "auto"            # auto 或具体串口号（COM3 / /dev/ttyUSB0）
    baudrate: int | None = None   # 留空则用配置默认


class DeviceStatusLatest(BaseModel):
    connected: bool = False
    reported_at: datetime | None = None
    battery_voltage: float | None = None
    sd_card_total_mb: int | None = None
    sd_card_used_mb: int | None = None
    uptime_seconds: int | None = None
    temperature: float | None = None
    humidity: float | None = None
    free_heap: int | None = None


class SyncResponse(BaseModel):
    success: bool
    synced_events: int = 0
    message: str = ""
