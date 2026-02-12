"""Tests for Telegram client."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from config import TelegramConfig
from telegram_client import TelegramClient, TelegramMessage, TelegramUpdate


class TestTelegramClientAsync:
    """Tests for async Telegram client."""

    @pytest.mark.asyncio
    async def test_get_me_async(self, mock_config: TelegramConfig):
        """Test getting bot information asynchronously."""
        mock_response = {
            "ok": True,
            "result": {
                "id": 123456,
                "is_bot": True,
                "first_name": "Test Bot",
                "username": "test_bot",
            },
        }

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value = mock_context

            async with TelegramClient(mock_config) as client:
                result = await client.get_me_async()

                assert result["id"] == 123456
                assert result["username"] == "test_bot"

    @pytest.mark.asyncio
    async def test_send_message_async(self, mock_config: TelegramConfig):
        """Test sending a message asynchronously."""
        mock_response = {
            "ok": True,
            "result": {
                "message_id": 1,
                "chat": {"id": 789, "type": "private"},
                "text": "Hello",
                "date": 1234567890,
                "from": {"id": 123, "username": "test_bot"},
            },
        }

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value = mock_context

            async with TelegramClient(mock_config) as client:
                message = await client.send_message_async(789, "Hello")

                assert message.message_id == 1
                assert message.chat_id == 789
                assert message.text == "Hello"

    @pytest.mark.asyncio
    async def test_get_updates_async(self, mock_config: TelegramConfig):
        """Test getting updates asynchronously."""
        mock_response = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 1,
                        "chat": {"id": 789, "type": "private"},
                        "text": "Test message",
                        "date": 1234567890,
                        "from": {"id": 456, "username": "user"},
                    },
                }
            ],
        }

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value = mock_context

            async with TelegramClient(mock_config) as client:
                updates = await client.get_updates_async()

                assert len(updates) == 1
                assert updates[0].update_id == 1
                assert updates[0].message is not None
                assert updates[0].message.text == "Test message"


class TestTelegramClientSync:
    """Tests for sync Telegram client."""

    def test_get_me_sync(self, sync_config: TelegramConfig):
        """Test getting bot information synchronously."""
        mock_response = {
            "ok": True,
            "result": {
                "id": 123456,
                "is_bot": True,
                "first_name": "Test Bot",
                "username": "test_bot",
            },
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response

            with TelegramClient(sync_config) as client:
                result = client.get_me_sync()

                assert result["id"] == 123456
                assert result["username"] == "test_bot"

    def test_send_message_sync(self, sync_config: TelegramConfig):
        """Test sending a message synchronously."""
        mock_response = {
            "ok": True,
            "result": {
                "message_id": 1,
                "chat": {"id": 789, "type": "private"},
                "text": "Hello",
                "date": 1234567890,
                "from": {"id": 123, "username": "test_bot"},
            },
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response

            with TelegramClient(sync_config) as client:
                message = client.send_message_sync(789, "Hello")

                assert message.message_id == 1
                assert message.chat_id == 789
                assert message.text == "Hello"

    def test_get_updates_sync(self, sync_config: TelegramConfig):
        """Test getting updates synchronously."""
        mock_response = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 1,
                        "chat": {"id": 789, "type": "private"},
                        "text": "Test message",
                        "date": 1234567890,
                        "from": {"id": 456, "username": "user"},
                    },
                }
            ],
        }

        with patch("requests.post") as mock_post:
            mock_post.return_value.json.return_value = mock_response

            with TelegramClient(sync_config) as client:
                updates = client.get_updates_sync()

                assert len(updates) == 1
                assert updates[0].update_id == 1
                assert updates[0].message is not None
                assert updates[0].message.text == "Test message"


class TestTelegramMessage:
    """Tests for TelegramMessage."""

    def test_from_dict(self):
        """Test creating TelegramMessage from dict."""
        data = {
            "message_id": 1,
            "chat": {"id": 789, "type": "private"},
            "text": "Hello",
            "date": 1234567890,
            "from": {"id": 123, "username": "test_user"},
        }

        message = TelegramMessage.from_dict(data)

        assert message.message_id == 1
        assert message.chat_id == 789
        assert message.text == "Hello"
        assert message.from_user_id == 123
        assert message.from_username == "test_user"


class TestTelegramUpdate:
    """Tests for TelegramUpdate."""

    def test_from_dict(self):
        """Test creating TelegramUpdate from dict."""
        data = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "chat": {"id": 789, "type": "private"},
                "text": "Hello",
                "date": 1234567890,
                "from": {"id": 123, "username": "test_user"},
            },
        }

        update = TelegramUpdate.from_dict(data)

        assert update.update_id == 1
        assert update.message is not None
        assert update.message.text == "Hello"
