"""日志管理路由：事件分页查询、详情、CSV 导出。"""
from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.trigger_event import TriggerEvent
from app.schemas.common import PageResult
from app.schemas.entities import TriggerEventOut

router = APIRouter()


def _apply_filters(stmt, start: datetime | None, end: datetime | None, sensor_id: str | None):
    if start is not None:
        stmt = stmt.where(TriggerEvent.event_time >= start)
    if end is not None:
        stmt = stmt.where(TriggerEvent.event_time <= end)
    if sensor_id:
        stmt = stmt.where(TriggerEvent.sensor_id == sensor_id)
    return stmt


@router.get("/events/export")
async def export_events(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    sensor_id: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    stmt = _apply_filters(select(TriggerEvent), start, end, sensor_id).order_by(
        TriggerEvent.event_time.desc())
    rows = (await session.execute(stmt)).scalars().all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "event_time", "sensor_id", "audio_file",
                     "temperature", "humidity", "battery_voltage"])
    for r in rows:
        writer.writerow([
            r.id, r.event_time.isoformat() if r.event_time else "",
            r.sensor_id, r.audio_file or "",
            r.temperature if r.temperature is not None else "",
            r.humidity if r.humidity is not None else "",
            r.battery_voltage if r.battery_voltage is not None else "",
        ])
    buf.seek(0)
    fname = f"trigger_events_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )


@router.get("/events", response_model=PageResult[TriggerEventOut])
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    sensor_id: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    count_stmt = _apply_filters(select(func.count()).select_from(TriggerEvent),
                                start, end, sensor_id)
    total = int((await session.execute(count_stmt)).scalar() or 0)

    stmt = _apply_filters(select(TriggerEvent), start, end, sensor_id) \
        .order_by(TriggerEvent.event_time.desc()) \
        .offset((page - 1) * page_size).limit(page_size)
    rows = (await session.execute(stmt)).scalars().all()

    return PageResult[TriggerEventOut](
        total=total,
        page=page,
        page_size=page_size,
        items=[TriggerEventOut.model_validate(r) for r in rows],
    )


@router.get("/events/{event_id}", response_model=TriggerEventOut)
async def get_event(event_id: int, session: AsyncSession = Depends(get_db)):
    from fastapi import HTTPException
    obj = await session.get(TriggerEvent, event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="事件不存在")
    return TriggerEventOut.model_validate(obj)
