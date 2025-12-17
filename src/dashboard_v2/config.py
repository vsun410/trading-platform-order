"""Configuration for Dashboard V2.

All settings are loaded from environment variables to comply with
Constitution VIII (No Hardcoding).
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Dashboard V2 configuration settings."""

    # Supabase
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")

    # Server
    host: str = Field(default="0.0.0.0", alias="DASHBOARD_HOST")
    port: int = Field(default=8502, alias="DASHBOARD_PORT")
    debug: bool = Field(default=False, alias="DASHBOARD_DEBUG")

    # Trading parameters (from config, not hardcoded)
    fee_rate: float = Field(
        default=0.0038,
        alias="FEE_RATE",
        description="Total fee rate: Upbit 0.1% + Binance 0.08% + Slippage 0.2%",
    )

    # API settings
    api_timeout: int = Field(default=10, alias="API_TIMEOUT")
    refresh_interval: int = Field(default=10, alias="REFRESH_INTERVAL")

    # Telegram (optional)
    telegram_bot_token: Optional[str] = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(default=None, alias="TELEGRAM_CHAT_ID")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
