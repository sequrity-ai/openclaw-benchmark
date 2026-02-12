"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from config import TelegramConfig


class TestTelegramConfig:
    """Tests for TelegramConfig."""

    def test_default_values(self):
        """Test configuration with default values."""
        config = TelegramConfig(telegram_bot_token="test_token")

        assert config.telegram_bot_token == "test_token"
        assert config.openclaw_bot_username == "openclaw_bot"
        assert config.async_mode is True
        assert config.request_timeout == 30
        assert config.polling_timeout == 10
        assert config.max_concurrent_sessions == 10
        assert config.log_level == "INFO"
        assert config.debug_mode is False

    def test_custom_values(self):
        """Test configuration with custom values."""
        config = TelegramConfig(
            telegram_bot_token="custom_token",
            openclaw_bot_username="custom_bot",
            async_mode=False,
            request_timeout=60,
            polling_timeout=20,
            max_concurrent_sessions=5,
            log_level="DEBUG",
            debug_mode=True,
        )

        assert config.telegram_bot_token == "custom_token"
        assert config.openclaw_bot_username == "custom_bot"
        assert config.async_mode is False
        assert config.request_timeout == 60
        assert config.polling_timeout == 20
        assert config.max_concurrent_sessions == 5
        assert config.log_level == "DEBUG"
        assert config.debug_mode is True

    def test_telegram_api_url(self):
        """Test telegram_api_url property."""
        config = TelegramConfig(telegram_bot_token="123456:ABC-DEF")

        expected = "https://api.telegram.org/bot123456:ABC-DEF"
        assert config.telegram_api_url == expected

    def test_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            TelegramConfig()

    def test_async_mode_flag(self):
        """Test async_mode flag behavior."""
        # Test async mode (default)
        config_async = TelegramConfig(telegram_bot_token="test", async_mode=True)
        assert config_async.async_mode is True

        # Test sync mode
        config_sync = TelegramConfig(telegram_bot_token="test", async_mode=False)
        assert config_sync.async_mode is False
