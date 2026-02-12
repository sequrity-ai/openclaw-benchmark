"""Configuration management for Telegram client."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramConfig(BaseSettings):
    """Telegram client configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram settings
    telegram_bot_token: str = Field(
        ...,
        description="Telegram bot token from BotFather",
    )
    openclaw_bot_username: str = Field(
        default="openclaw_bot",
        description="Username of the OpenClaw bot to interact with",
    )

    # Performance settings
    async_mode: bool = Field(
        default=True,
        description="Enable async mode for performance (True) or sync mode for debugging (False)",
    )

    # API settings
    telegram_api_base_url: str = Field(
        default="https://api.telegram.org",
        description="Telegram API base URL",
    )
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
    )
    polling_timeout: int = Field(
        default=10,
        description="Long polling timeout in seconds",
    )
    polling_interval: float = Field(
        default=1.0,
        description="Interval between polling attempts in seconds",
    )

    # Benchmark settings
    max_concurrent_sessions: int = Field(
        default=10,
        description="Maximum concurrent sessions for benchmarking (async mode only)",
    )
    default_session_timeout: int = Field(
        default=300,
        description="Default session timeout in seconds",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable detailed debug logging",
    )

    @property
    def telegram_api_url(self) -> str:
        """Get the full Telegram API URL with bot token."""
        return f"{self.telegram_api_base_url}/bot{self.telegram_bot_token}"


def load_config() -> TelegramConfig:
    """Load configuration from environment variables and .env file."""
    return TelegramConfig()
