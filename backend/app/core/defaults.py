"""默认设备配置种子（幂等写入）。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device_config import DeviceConfig

# 与前端配置页、串口 set_config 协议保持一致的键名
DEFAULT_CONFIG: dict[str, str] = {
    "volume": "80",               # 播放音量 0-100
    "trigger_interval": "60",     # 触发最小间隔（秒）
    "schedule_enabled": "0",      # 定时播放开关 0/1
    "schedule_interval": "30",    # 定时播放间隔（分钟）
}


async def seed_default_config(session: AsyncSession) -> None:
    """仅在缺失时写入默认配置，不覆盖用户已修改的值。"""
    existing = set(
        (await session.execute(select(DeviceConfig.config_key))).scalars().all()
    )
    for key, value in DEFAULT_CONFIG.items():
        if key not in existing:
            session.add(DeviceConfig(config_key=key, config_value=value))
