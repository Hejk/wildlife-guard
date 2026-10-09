"""设备状态与串口控制路由：连接、断开、状态、同步。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.serial_client import serial_client
from app.models.device_status import DeviceStatus
from app.schemas.device import ConnectRequest, DeviceStatusLatest, SyncResponse
from app.services import sync_service

router = APIRouter()


@router.get("/ports")
async def list_ports():
    """列出可用串口，供前端选择。"""
    return {"ports": serial_client.list_ports()}


@router.post("/connect")
async def connect(req: ConnectRequest):
    serial_client.port = req.port or "auto"
    if req.baudrate:
        serial_client.baudrate = req.baudrate
    ok = await serial_client.connect()
    if not ok:
        raise HTTPException(status_code=400, detail="串口连接失败：请检查 USB 连接与串口号")
    return {"connected": True, "port": serial_client.port, "baudrate": serial_client.baudrate}


@router.post("/disconnect")
async def disconnect():
    await serial_client.disconnect()
    return {"connected": False}


@router.get("/status", response_model=DeviceStatusLatest)
async def get_status(session: AsyncSession = Depends(get_db)):
    snap = (await session.execute(
        select(DeviceStatus).order_by(DeviceStatus.reported_at.desc()).limit(1)
    )).scalars().first()

    out = DeviceStatusLatest(connected=serial_client.connected)
    if snap:
        out.reported_at = snap.reported_at
        out.battery_voltage = snap.battery_voltage
        out.sd_card_total_mb = snap.sd_card_total_mb
        out.sd_card_used_mb = snap.sd_card_used_mb
        out.uptime_seconds = snap.uptime_seconds
        out.temperature = snap.temperature
        out.humidity = snap.humidity
    return out


@router.post("/sync", response_model=SyncResponse)
async def sync(session: AsyncSession = Depends(get_db)):
    if not serial_client.connected:
        raise HTTPException(status_code=400, detail="设备未连接，请先连接串口")
    try:
        count = await sync_service.sync_events(session)
        await sync_service.fetch_status(session)
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=502, detail=f"串口通信失败: {e}")
    return SyncResponse(success=True, synced_events=count, message="同步完成")
