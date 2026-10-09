"""设备配置路由：读取 / 更新（在线时同步下发到 ESP32）。"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.serial_client import serial_client
from app.models.device_config import DeviceConfig
from app.schemas.config import ConfigResponse, ConfigUpdateRequest, ConfigUpdateResponse

router = APIRouter()


async def _load_config(session: AsyncSession) -> dict[str, str]:
    rows = (await session.execute(select(DeviceConfig))).scalars().all()
    return {r.config_key: (r.config_value or "") for r in rows}


@router.get("", response_model=ConfigResponse)
async def get_config(session: AsyncSession = Depends(get_db)):
    return ConfigResponse(config=await _load_config(session), device_online=serial_client.connected)


@router.put("", response_model=ConfigUpdateResponse)
async def update_config(
    payload: ConfigUpdateRequest,
    session: AsyncSession = Depends(get_db),
):
    # 1) upsert 到本地 DB
    existing = {
        r.config_key: r for r in (await session.execute(select(DeviceConfig))).scalars().all()
    }
    for key, value in payload.items.items():
        if key in existing:
            existing[key].config_value = str(value)
            existing[key].updated_at = datetime.utcnow()
        else:
            session.add(DeviceConfig(config_key=key, config_value=str(value)))
    await session.commit()

    # 2) 设备在线时下发
    pushed = False
    if payload.push_to_device and serial_client.connected:
        pushed = True
        for key, value in payload.items.items():
            try:
                ok = await serial_client.set_config(key, str(value))
                pushed = pushed and ok
            except (ConnectionError, TimeoutError):
                pushed = False

    return ConfigUpdateResponse(
        saved=True,
        pushed_to_device=pushed,
        config=await _load_config(session),
    )
