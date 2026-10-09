"""AI 预留路由：分析触发数据（后续接入大模型）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.trigger_event import TriggerEvent
from app.services.ai_service import ai_service

router = APIRouter()


class AnalyzeRequest(BaseModel):
    event_id: int | None = None


@router.post("/analyze")
async def analyze(req: AnalyzeRequest, session: AsyncSession = Depends(get_db)):
    if not ai_service.enabled:
        return {"status": "disabled", "message": "AI API key not configured"}

    event_data: dict = {}
    if req.event_id:
        obj = await session.get(TriggerEvent, req.event_id)
        if not obj:
            raise HTTPException(status_code=404, detail="事件不存在")
        event_data = {
            "id": obj.id,
            "event_time": obj.event_time.isoformat() if obj.event_time else None,
            "sensor_id": obj.sensor_id,
            "audio_file": obj.audio_file,
            "temperature": obj.temperature,
            "humidity": obj.humidity,
            "battery_voltage": obj.battery_voltage,
        }

    try:
        return await ai_service.analyze_event(event_data)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="AI 分析能力待接入")
