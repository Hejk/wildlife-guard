"""FastAPI 应用入口 - 智哨（Smart Sentinel）管理后台 V1（USB 近场同步模式）。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, audio, config, dashboard, device, logs
from app.core.config import get_settings
from app.core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库并写入默认配置
    await init_db()
    yield


app = FastAPI(
    title="智哨 (Smart Sentinel) - 基于端云协同的农田生态防御系统管理后台",
    version="1.0.0",
    description="V1版本 - USB近场同步模式（方案A）",
    lifespan=lifespan,
)

# CORS - 允许前端跨域访问
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["数据看板"])
app.include_router(audio.router, prefix="/api/audio", tags=["音频管理"])
app.include_router(logs.router, prefix="/api/logs", tags=["日志管理"])
app.include_router(config.router, prefix="/api/config", tags=["设备配置"])
app.include_router(device.router, prefix="/api/device", tags=["设备状态"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI预留"])


@app.get("/")
async def root():
    return {"message": "Smart Sentinel API V1 · 智哨：基于端云协同的农田生态防御系统", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health():
    return {"status": "ok"}
