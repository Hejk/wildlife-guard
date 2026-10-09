"""数据看板路由：概览 + 趋势。"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.trigger_event import TriggerEvent
from app.schemas.dashboard import (
    DashboardOverview,
    DashboardTrends,
    SensorCount,
    TrendPoint,
)
from app.schemas.entities import TriggerEventOut

router = APIRouter()


async def _count(session: AsyncSession, since: datetime | None = None) -> int:
    stmt = select(func.count()).select_from(TriggerEvent)
    if since is not None:
        stmt = stmt.where(TriggerEvent.event_time >= since)
    return int((await session.execute(stmt)).scalar() or 0)


@router.get("/overview", response_model=DashboardOverview)
async def overview(session: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)

    today_count = await _count(session, today_start)
    week_count = await _count(session, week_start)
    total_count = await _count(session, None)

    dist_rows = (await session.execute(
        select(TriggerEvent.sensor_id, func.count())
        .group_by(TriggerEvent.sensor_id)
    )).all()
    sensor_distribution = [SensorCount(sensor_id=r[0], count=r[1]) for r in dist_rows]

    recent = (await session.execute(
        select(TriggerEvent).order_by(TriggerEvent.event_time.desc()).limit(10)
    )).scalars().all()

    return DashboardOverview(
        today_count=today_count,
        week_count=week_count,
        total_count=total_count,
        sensor_distribution=sensor_distribution,
        recent_events=[TriggerEventOut.model_validate(e) for e in recent],
    )


@router.get("/trends", response_model=DashboardTrends)
async def trends(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    limit: int = Query(14, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    now = datetime.utcnow()
    if granularity == "day":
        start = now - timedelta(days=limit)
        fmt = "%Y-%m-%d"
    elif granularity == "week":
        start = now - timedelta(weeks=limit)
        fmt = "%Y-%GW%V"
    else:  # month
        start = now - timedelta(days=limit * 30)
        fmt = "%Y-%m"

    rows = (await session.execute(
        select(TriggerEvent.event_time).where(TriggerEvent.event_time >= start)
    )).scalars().all()

    buckets: dict[str, int] = {}
    for et in rows:
        key = et.strftime(fmt)
        buckets[key] = buckets.get(key, 0) + 1

    # 生成连续时间轴（含空桶）
    points: list[TrendPoint] = []
    if granularity == "day":
        cur = start.replace(hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(days=1)
        for _ in range(limit + 1):
            points.append(TrendPoint(label=cur.strftime(fmt), count=buckets.get(cur.strftime(fmt), 0)))
            cur += step
    else:
        for label in sorted(buckets.keys()):
            points.append(TrendPoint(label=label, count=buckets[label]))

    return DashboardTrends(granularity=granularity, points=points)
