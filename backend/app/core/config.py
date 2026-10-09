"""全局配置：从环境变量 / .env 读取，带合理默认值。"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 串口
    serial_port: str = "auto"
    serial_baudrate: int = 115200

    # 数据库
    database_url: str = "sqlite+aiosqlite:///../database/wildlife.db"

    # AI 预留
    ai_api_key: str | None = None
    ai_base_url: str | None = None

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
