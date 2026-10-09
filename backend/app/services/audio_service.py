"""音频文件管理：本地存储 + 通过串口同步到 ESP32 SD 卡。"""
from __future__ import annotations

import io
import os
import wave
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.serial_client import serial_client
from app.models.audio_file import AudioFile

# 本地音频存储目录：<project_root>/storage/audio
STORAGE_DIR = Path(__file__).resolve().parents[3] / "storage" / "audio"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_name(filename: str) -> str:
    """只取 basename，防止路径穿越。"""
    return os.path.basename(filename or "").strip()


def _wav_duration(data: bytes) -> int | None:
    """尽力解析 WAV 时长（秒）；非 WAV 返回 None。"""
    try:
        with wave.open(io.BytesIO(data), "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate() or 1
            return int(frames / rate)
    except Exception:
        return None


async def list_files(session: AsyncSession) -> list[AudioFile]:
    res = await session.execute(select(AudioFile).order_by(AudioFile.id.desc()))
    return list(res.scalars().all())


async def get(session: AsyncSession, audio_id: int) -> AudioFile | None:
    return await session.get(AudioFile, audio_id)


async def save_upload(
    session: AsyncSession,
    filename: str,
    content: bytes,
    category: str = "通用驱赶",
) -> AudioFile:
    """保存上传的音频到本地磁盘并登记（status=local）。"""
    name = _safe_name(filename)
    if not name:
        raise ValueError("非法文件名")

    # 同名覆盖磁盘文件
    disk_path = STORAGE_DIR / name
    with open(disk_path, "wb") as f:
        f.write(content)

    existing = (await session.execute(
        select(AudioFile).where(AudioFile.filename == name))).scalar_one_or_none()

    if existing:
        existing.category = category
        existing.file_size = len(content)
        existing.duration_seconds = _wav_duration(content)
        existing.status = "local"
        existing.uploaded_at = datetime.utcnow()
        await session.commit()
        await session.refresh(existing)
        return existing

    rec = AudioFile(
        filename=name,
        category=category,
        file_size=len(content),
        duration_seconds=_wav_duration(content),
        status="local",
        uploaded_at=datetime.utcnow(),
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return rec


async def delete(session: AsyncSession, audio_id: int) -> dict | None:
    """删除音频：本地文件 + 设备在线时同步删除 SD 卡文件。

    记录保留并置 status=deleted（与蓝图 local/synced/deleted 语义一致，同名重传可复活）；
    设备端删除失败不阻塞本地删除。返回 None 表示记录不存在。
    """
    rec = await session.get(AudioFile, audio_id)
    if not rec:
        return None

    # 1) 删除本地磁盘文件
    disk_path = STORAGE_DIR / _safe_name(rec.filename)
    if disk_path.exists():
        try:
            os.remove(disk_path)
        except OSError:
            pass

    # 2) 设备在线时同步删除 SD 卡上的文件
    device_deleted = False
    if serial_client.connected:
        try:
            device_deleted = await serial_client.delete_audio(rec.filename)
        except (ConnectionError, TimeoutError) as e:
            print(f"设备端删除音频失败: {e}")

    # 3) 记录标记为已删除
    rec.status = "deleted"
    await session.commit()
    await session.refresh(rec)
    return {"record": rec, "device_deleted": device_deleted}


async def sync_to_device(session: AsyncSession, audio_id: int) -> bool:
    """通过串口把本地音频推送到 SD 卡，成功后置 status=synced。"""
    rec = await session.get(AudioFile, audio_id)
    if not rec:
        raise FileNotFoundError("音频记录不存在")
    disk_path = STORAGE_DIR / _safe_name(rec.filename)
    if not disk_path.exists():
        raise FileNotFoundError("本地音频文件缺失")

    with open(disk_path, "rb") as f:
        data = f.read()

    ok = await serial_client.upload_audio(rec.filename, data)
    if ok:
        rec.status = "synced"
        rec.uploaded_at = datetime.utcnow()
        await session.commit()
        await session.refresh(rec)
    return ok
