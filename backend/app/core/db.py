"""数据库连接（SQLAlchemy 2.0 async engine + 同步 engine 用于建表）。"""
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

Base = declarative_base()

_settings = get_settings()
DATABASE_URL = _settings.database_url

# 确保 SQLite 数据目录存在
if DATABASE_URL.startswith("sqlite"):
    _db_path = DATABASE_URL.split("///")[-1]
    _dir = os.path.dirname(os.path.abspath(_db_path))
    os.makedirs(_dir, exist_ok=True)

# 异步引擎（运行时）
async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# 同步引擎（仅用于 startup 建表；将 aiosqlite 驱动换回原生 sqlite）
_sync_url = DATABASE_URL.replace("+aiosqlite", "")
sync_engine = create_engine(_sync_url, echo=False)


async def init_db() -> None:
    """初始化数据库 - 创建所有表并写入默认配置。"""
    from app import models  # noqa: F401  确保模型已注册
    from app.core.defaults import seed_default_config

    # 使用同步引擎建表（简单可靠）
    Base.metadata.create_all(sync_engine)
    # 默认配置写入（幂等）
    async with AsyncSessionLocal() as session:
        await seed_default_config(session)
        await session.commit()


async def get_db() -> AsyncSession:
    """FastAPI 依赖：获取数据库会话。"""
    async with AsyncSessionLocal() as session:
        yield session
