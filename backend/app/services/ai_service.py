"""AI 服务预留接口，后续接入大模型做动物识别 / 数据分析。

未配置 API Key 时优雅降级，不影响 V1 主流程。
Key 通过环境变量注入：AI_API_KEY / AI_BASE_URL（见 backend/.env.example）。
"""
from __future__ import annotations

from app.core.config import get_settings


class AIService:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        s = get_settings()
        self.api_key = api_key or s.ai_api_key
        self.base_url = base_url or s.ai_base_url

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def analyze_event(self, event_data: dict) -> dict:
        """分析触发事件，后续接入大模型。"""
        if not self.enabled:
            return {"status": "disabled", "message": "AI API key not configured"}
        # TODO: 接入大模型 API 做动物种类识别 / 行为分析
        raise NotImplementedError("AI 分析能力待接入")

    async def generate_report(self, events: list) -> dict:
        """生成周期分析报告。"""
        if not self.enabled:
            return {"status": "disabled", "message": "AI API key not configured"}
        # TODO: 接入大模型生成分析报告
        raise NotImplementedError("AI 报告生成能力待接入")


# 全局 AI 服务实例
ai_service = AIService()
