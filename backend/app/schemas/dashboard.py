"""数据看板相关 schema。"""
from __future__ import annotations

from pydantic import BaseModel

from app.schemas.entities import TriggerEventOut


class SensorCount(BaseModel):
    sensor_id: str
    count: int


class DashboardOverview(BaseModel):
    today_count: int = 0
    week_count: int = 0
    total_count: int = 0
    sensor_distribution: list[SensorCount] = []
    recent_events: list[TriggerEventOut] = []


class TrendPoint(BaseModel):
    label: str      # 日期/周/月标签
    count: int


class DashboardTrends(BaseModel):
    granularity: str        # day / week / month
    points: list[TrendPoint] = []
