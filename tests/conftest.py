"""Pytest configuration and fixtures."""

import pytest

from config import TelegramConfig


@pytest.fixture
def mock_config() -> TelegramConfig:
    """Create a mock configuration for testing."""
    return TelegramConfig(
        telegram_bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
        openclaw_bot_username="test_bot",
        async_mode=True,
        debug_mode=True,
    )


@pytest.fixture
def sync_config(mock_config: TelegramConfig) -> TelegramConfig:
    """Create a sync mode configuration for testing."""
    mock_config.async_mode = False
    return mock_config
