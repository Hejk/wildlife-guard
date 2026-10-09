"""音频管理路由：列表、上传、删除、同步到设备。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.serial_client import serial_client
from app.schemas.entities import AudioFileOut
from app.services import audio_service

router = APIRouter()


@router.get("/files", response_model=list[AudioFileOut])
async def list_files(session: AsyncSession = Depends(get_db)):
    rows = await audio_service.list_files(session)
    return [AudioFileOut.model_validate(r) for r in rows]


@router.post("/upload", response_model=AudioFileOut)
async def upload(
    file: UploadFile = File(...),
    category: str = Form("通用驱赶"),
    session: AsyncSession = Depends(get_db),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="空文件")
    rec = await audio_service.save_upload(session, file.filename or "audio.wav", content, category)
    return AudioFileOut.model_validate(rec)


@router.delete("/{audio_id}")
async def delete(audio_id: int, session: AsyncSession = Depends(get_db)):
    result = await audio_service.delete(session, audio_id)
    if result is None:
        raise HTTPException(status_code=404, detail="音频不存在")
    rec = result["record"]
    return {
        "success": True,
        "status": "ok",
        "message": f"已删除 {rec.filename}",
        "device_deleted": result["device_deleted"],
    }


@router.get("/device-list")
async def device_list():
    """列出 SD 卡上的音频文件，供后台与本地对账。"""
    if not serial_client.connected:
        raise HTTPException(status_code=400, detail="设备未连接，请先通过 /api/device/connect 建立串口连接")
    try:
        files = await serial_client.list_audio()
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=502, detail=f"串口通信失败: {e}")
    return {"status": "ok", "files": files}


@router.post("/sync/{audio_id}")
async def sync_to_device(audio_id: int, session: AsyncSession = Depends(get_db)):
    if not serial_client.connected:
        raise HTTPException(status_code=400, detail="设备未连接，请先通过 /api/device/connect 建立串口连接")
    try:
        ok = await audio_service.sync_to_device(session, audio_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(status_code=502, detail=f"串口通信失败: {e}")
    if not ok:
        raise HTTPException(status_code=502, detail="设备未确认接收成功")
    return {"success": True}
