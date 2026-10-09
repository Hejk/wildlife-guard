"""设备配置相关 schema。"""
from __future__ import annotations

from pydantic import BaseModel


class ConfigResponse(BaseModel):
    config: dict[str, str]
    device_online: bool = False


class ConfigUpdateRequest(BaseModel):
    """键值对形式的配置更新。"""
    items: dict[str, str]
    push_to_device: bool = True   # 设备在线时是否同步下发到 ESP32


class ConfigUpdateResponse(BaseModel):
    saved: bool
    pushed_to_device: bool = False
    config: dict[str, str] = {}
