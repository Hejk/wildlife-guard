"""Pydantic schema 汇总导出。"""
from app.schemas.common import ApiResponse, PageResult
from app.schemas.entities import (
    TriggerEventOut,
    TriggerEventCreate,
    AudioFileOut,
    DeviceConfigOut,
    DeviceStatusOut,
)
from app.schemas.dashboard import (
    DashboardOverview,
    DashboardTrends,
    SensorCount,
    TrendPoint,
)
from app.schemas.device import ConnectRequest, DeviceStatusLatest, SyncResponse
from app.schemas.config import (
    ConfigResponse,
    ConfigUpdateRequest,
    ConfigUpdateResponse,
)

__all__ = [
    "ApiResponse",
    "PageResult",
    "TriggerEventOut",
    "TriggerEventCreate",
    "AudioFileOut",
    "DeviceConfigOut",
    "DeviceStatusOut",
    "DashboardOverview",
    "DashboardTrends",
    "SensorCount",
    "TrendPoint",
    "ConnectRequest",
    "DeviceStatusLatest",
    "SyncResponse",
    "ConfigResponse",
    "ConfigUpdateRequest",
    "ConfigUpdateResponse",
]
