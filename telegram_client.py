"""Telegram Bot API client with dual-mode (async/sync) support."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

import aiohttp
import requests

from config import TelegramConfig

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """Represents a Telegram message."""

    message_id: int
    chat_id: int
    text: str | None
    from_user_id: int | None
    from_username: str | None
    date: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelegramMessage":
        """Create a TelegramMessage from API response dict."""
        from_user = data.get("from", {})
        return cls(
            message_id=data["message_id"],
            chat_id=data["chat"]["id"],
            text=data.get("text"),
            from_user_id=from_user.get("id"),
            from_username=from_user.get("username"),
            date=data["date"],
        )


@dataclass
class TelegramUpdate:
    """Represents a Telegram update."""

    update_id: int
    message: TelegramMessage | None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelegramUpdate":
        """Create a TelegramUpdate from API response dict."""
        message = None
        if "message" in data:
            message = TelegramMessage.from_dict(data["message"])
        return cls(update_id=data["update_id"], message=message)


class TelegramClient:
    """Telegram Bot API client with sync/async support."""

    def __init__(self, config: TelegramConfig):
        """Initialize the Telegram client.

        Args:
            config: Telegram configuration
        """
        self.config = config
        self.base_url = config.telegram_api_url
        self._offset: int = 0
        self._session: aiohttp.ClientSession | None = None
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging based on configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        if self.config.debug_mode:
            logger.setLevel(logging.DEBUG)

    async def __aenter__(self) -> "TelegramClient":
        """Async context manager entry."""
        if self.config.async_mode:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def __enter__(self) -> "TelegramClient":
        """Sync context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Sync context manager exit."""
        pass

    async def _make_request_async(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make an async HTTP request to Telegram API.

        Args:
            method: API method name
            params: Request parameters

        Returns:
            API response data

        Raises:
            ValueError: If the request fails
        """
        if not self._session:
            raise RuntimeError("Session not initialized. Use async context manager.")

        url = f"{self.base_url}/{method}"
        logger.debug(f"Async request to {method} with params: {params}")

        try:
            async with self._session.post(
                url, json=params, timeout=self.config.request_timeout
            ) as response:
                data = await response.json()
                if not data.get("ok"):
                    error_msg = data.get("description", "Unknown error")
                    raise ValueError(f"Telegram API error: {error_msg}")
                return data.get("result", {})
        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout for {method}")
            raise ValueError(f"Request timeout: {e}")
        except Exception as e:
            logger.error(f"Request failed for {method}: {e}")
            raise

    def _make_request_sync(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a sync HTTP request to Telegram API.

        Args:
            method: API method name
            params: Request parameters

        Returns:
            API response data

        Raises:
            ValueError: If the request fails
        """
        url = f"{self.base_url}/{method}"
        logger.debug(f"Sync request to {method} with params: {params}")

        try:
            response = requests.post(url, json=params, timeout=self.config.request_timeout)
            data = response.json()
            if not data.get("ok"):
                error_msg = data.get("description", "Unknown error")
                raise ValueError(f"Telegram API error: {error_msg}")
            return data.get("result", {})
        except requests.Timeout as e:
            logger.error(f"Request timeout for {method}")
            raise ValueError(f"Request timeout: {e}")
        except Exception as e:
            logger.error(f"Request failed for {method}: {e}")
            raise

    async def send_message_async(
        self, chat_id: int, text: str, reply_to_message_id: int | None = None
    ) -> TelegramMessage:
        """Send a message asynchronously.

        Args:
            chat_id: Chat ID to send message to
            text: Message text
            reply_to_message_id: Optional message ID to reply to

        Returns:
            Sent message
        """
        params: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id

        result = await self._make_request_async("sendMessage", params)
        return TelegramMessage.from_dict(result)

    def send_message_sync(
        self, chat_id: int, text: str, reply_to_message_id: int | None = None
    ) -> TelegramMessage:
        """Send a message synchronously.

        Args:
            chat_id: Chat ID to send message to
            text: Message text
            reply_to_message_id: Optional message ID to reply to

        Returns:
            Sent message
        """
        params: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id

        result = self._make_request_sync("sendMessage", params)
        return TelegramMessage.from_dict(result)

    async def get_updates_async(self) -> list[TelegramUpdate]:
        """Get updates asynchronously using long polling.

        Returns:
            List of updates
        """
        params = {
            "offset": self._offset,
            "timeout": self.config.polling_timeout,
            "allowed_updates": ["message"],
        }

        result = await self._make_request_async("getUpdates", params)

        updates = [TelegramUpdate.from_dict(update) for update in result]

        # Update offset for next poll
        if updates:
            self._offset = max(update.update_id for update in updates) + 1

        return updates

    def get_updates_sync(self) -> list[TelegramUpdate]:
        """Get updates synchronously using long polling.

        Returns:
            List of updates
        """
        params = {
            "offset": self._offset,
            "timeout": self.config.polling_timeout,
            "allowed_updates": ["message"],
        }

        result = self._make_request_sync("getUpdates", params)

        updates = [TelegramUpdate.from_dict(update) for update in result]

        # Update offset for next poll
        if updates:
            self._offset = max(update.update_id for update in updates) + 1

        return updates

    async def send_message_to_bot_async(self, text: str) -> TelegramMessage:
        """Send a message to the configured OpenClaw bot asynchronously.

        Args:
            text: Message text

        Returns:
            Sent message

        Note:
            This requires knowing the bot's chat_id, which may need to be
            obtained through getUpdates or by starting a conversation first.
        """
        # Note: In practice, you'd need to get the bot's chat_id first
        # This is a placeholder that assumes you have the chat_id
        raise NotImplementedError(
            "You need to start a conversation with the bot first to get chat_id"
        )

    def send_message_to_bot_sync(self, text: str) -> TelegramMessage:
        """Send a message to the configured OpenClaw bot synchronously.

        Args:
            text: Message text

        Returns:
            Sent message

        Note:
            This requires knowing the bot's chat_id, which may need to be
            obtained through getUpdates or by starting a conversation first.
        """
        # Note: In practice, you'd need to get the bot's chat_id first
        # This is a placeholder that assumes you have the chat_id
        raise NotImplementedError(
            "You need to start a conversation with the bot first to get chat_id"
        )

    async def get_me_async(self) -> dict[str, Any]:
        """Get bot information asynchronously.

        Returns:
            Bot information
        """
        return await self._make_request_async("getMe")

    def get_me_sync(self) -> dict[str, Any]:
        """Get bot information synchronously.

        Returns:
            Bot information
        """
        return self._make_request_sync("getMe")


class TelegramSession:
    """Manages a conversation session with a Telegram bot."""

    def __init__(self, client: TelegramClient, chat_id: int):
        """Initialize a Telegram session.

        Args:
            client: Telegram client
            chat_id: Chat ID for this session
        """
        self.client = client
        self.chat_id = chat_id
        self.messages: list[TelegramMessage] = []
        self.start_time = time.time()

    async def send_message_async(
        self, text: str, wait_for_response: bool = True, timeout: float = 30.0
    ) -> TelegramMessage | None:
        """Send a message and optionally wait for a response.

        Args:
            text: Message text
            wait_for_response: Whether to wait for a response
            timeout: Maximum time to wait for response in seconds

        Returns:
            Response message if wait_for_response is True, else None
        """
        sent_msg = await self.client.send_message_async(self.chat_id, text)
        self.messages.append(sent_msg)
        logger.info(f"Sent message: {text[:50]}...")

        if wait_for_response:
            response = await self._wait_for_response_async(timeout)
            if response:
                self.messages.append(response)
            return response

        return None

    def send_message_sync(
        self, text: str, wait_for_response: bool = True, timeout: float = 30.0
    ) -> TelegramMessage | None:
        """Send a message and optionally wait for a response (sync).

        Args:
            text: Message text
            wait_for_response: Whether to wait for a response
            timeout: Maximum time to wait for response in seconds

        Returns:
            Response message if wait_for_response is True, else None
        """
        sent_msg = self.client.send_message_sync(self.chat_id, text)
        self.messages.append(sent_msg)
        logger.info(f"Sent message: {text[:50]}...")

        if wait_for_response:
            response = self._wait_for_response_sync(timeout)
            if response:
                self.messages.append(response)
            return response

        return None

    async def _wait_for_response_async(self, timeout: float) -> TelegramMessage | None:
        """Wait for a response from the bot asynchronously.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Response message or None if timeout
        """
        start_time = time.time()
        last_message_time = self.messages[-1].date if self.messages else 0

        while time.time() - start_time < timeout:
            updates = await self.client.get_updates_async()

            for update in updates:
                if (
                    update.message
                    and update.message.chat_id == self.chat_id
                    and update.message.date > last_message_time
                    and update.message.from_username == self.client.config.openclaw_bot_username
                ):
                    logger.info(f"Received response: {update.message.text[:50]}...")
                    return update.message

            await asyncio.sleep(self.client.config.polling_interval)

        logger.warning(f"Response timeout after {timeout}s")
        return None

    def _wait_for_response_sync(self, timeout: float) -> TelegramMessage | None:
        """Wait for a response from the bot synchronously.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Response message or None if timeout
        """
        start_time = time.time()
        last_message_time = self.messages[-1].date if self.messages else 0

        while time.time() - start_time < timeout:
            updates = self.client.get_updates_sync()

            for update in updates:
                if (
                    update.message
                    and update.message.chat_id == self.chat_id
                    and update.message.date > last_message_time
                    and update.message.from_username == self.client.config.openclaw_bot_username
                ):
                    logger.info(f"Received response: {update.message.text[:50]}...")
                    return update.message

            time.sleep(self.client.config.polling_interval)

        logger.warning(f"Response timeout after {timeout}s")
        return None

    def get_duration(self) -> float:
        """Get the duration of the session in seconds."""
        return time.time() - self.start_time
