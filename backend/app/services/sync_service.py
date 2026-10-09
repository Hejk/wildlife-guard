"""数据同步业务逻辑：通过 USB 串口从 ESP32 拉取日志与设备状态。"""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.serial_client import serial_client
from app.models.trigger_event import TriggerEvent
from app.models.device_status import DeviceStatus
from app.schemas.entities import TriggerEventCreate


def _pick(data: dict, *keys, default=None):
    """从多个候选字段名中取第一个存在的值（兼容协议短/长命名）。"""
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return default


async def sync_events(session: AsyncSession, since: datetime | None = None) -> int:
    """增量同步触发日志。返回新插入的记录数。"""
    if since is None:
        last = await session.execute(select(TriggerEvent.event_time).order_by(
            TriggerEvent.event_time.desc()).limit(1))
        last_time = last.scalar_one_or_none()
        since = last_time if last_time else datetime.min.replace(year=2000)

    raw_logs = await serial_client.sync_logs(since=since.isoformat())

    # 去重：已存在的 (event_time, sensor_id)
    existing = set(
        (await session.execute(select(TriggerEvent.event_time, TriggerEvent.sensor_id)))
        .all()
    )

    inserted = 0
    now = datetime.utcnow()
    for raw in raw_logs:
        try:
            evt = TriggerEventCreate(**raw)
        except Exception:
            continue  # 跳过非法记录
        if (evt.event_time, evt.sensor_id) in existing:
            continue
        session.add(TriggerEvent(
            event_time=evt.event_time,
            sensor_id=evt.sensor_id,
            audio_file=evt.audio_file,
            temperature=evt.temperature,
            humidity=evt.humidity,
            battery_voltage=evt.battery_voltage,
            synced_at=now,
        ))
        existing.add((evt.event_time, evt.sensor_id))
        inserted += 1

    await session.commit()
    return inserted


async def fetch_status(session: AsyncSession) -> dict:
    """拉取并保存设备状态快照，返回标准化字段。"""
    raw = await serial_client.get_status()
    normalized = {
        "battery_voltage": _pick(raw, "battery_voltage", "battery"),
        "sd_card_total_mb": _pick(raw, "sd_total_mb", "sd_total"),
        "sd_card_used_mb": _pick(raw, "sd_used_mb", "sd_used"),
        "uptime_seconds": _pick(raw, "uptime_seconds", "uptime"),
        "temperature": _pick(raw, "temperature", "temp"),
        "humidity": _pick(raw, "humidity"),
        "free_heap": _pick(raw, "free_heap"),
    }
    snap = DeviceStatus(
        reported_at=datetime.utcnow(),
        battery_voltage=normalized["battery_voltage"],
        sd_card_total_mb=normalized["sd_card_total_mb"],
        sd_card_used_mb=normalized["sd_card_used_mb"],
        uptime_seconds=normalized["uptime_seconds"],
        temperature=normalized["temperature"],
        humidity=normalized["humidity"],
    )
    session.add(snap)
    await session.commit()
    return normalized
