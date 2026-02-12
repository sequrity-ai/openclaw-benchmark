# Quick Start Guide

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Telegram bot token from [@BotFather](https://t.me/BotFather)

## Installation

```bash
# Clone/navigate to the project
cd opencalw-sandbox

# Sync dependencies (creates .venv automatically)
uv sync

# Or sync with dev dependencies
uv sync --group dev
```

## Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your bot token
# TELEGRAM_BOT_TOKEN=your_token_here
```

## Usage with uv

### Run CLI commands

```bash
# Test connection
uv run openclaw-tg test

# List available scenarios
uv run openclaw-tg list-scenarios

# Send a message (requires chat_id)
uv run openclaw-tg send <chat_id> "Hello!"

# Run benchmark
uv run openclaw-tg benchmark <chat_id> --scenario 0

# Use sync mode for debugging
uv run openclaw-tg --sync test

# Use async mode for performance
uv run openclaw-tg --async benchmark <chat_id> --scenario 0

# Verbose logging
uv run openclaw-tg -v test
```

### Run tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_telegram_client.py

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

### Run Python scripts directly

```bash
# Using uv run
uv run python -c "from config import load_config; print(load_config())"

# Or activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate   # On Windows

# Then run normally
python cli.py test
pytest -v
```

## Getting Your Chat ID

You need a chat ID to send messages. Here's how:

```bash
# 1. Start a chat with your bot on Telegram
# 2. Send any message to the bot
# 3. Run this command to get the chat ID:

uv run python -c "
import asyncio
from config import load_config
from telegram_client import TelegramClient

async def main():
    config = load_config()
    async with TelegramClient(config) as client:
        updates = await client.get_updates_async()
        for update in updates:
            if update.message:
                print(f'Chat ID: {update.message.chat_id}')
                print(f'From: {update.message.from_username}')

asyncio.run(main())
"
```

## Development Workflow

```bash
# 1. Install with dev dependencies
uv sync --group dev

# 2. Make changes to code
# 3. Run tests
uv run pytest -v

# 4. Format and lint (optional)
uv run ruff check .
uv run ruff format .

# 5. Run integration tests
uv run openclaw-tg test
```

## Common Commands Reference

| Task | Command |
|------|---------|
| Install dependencies | `uv sync` |
| Install with dev deps | `uv sync --group dev` |
| Update dependencies | `uv sync --upgrade` |
| Run CLI | `uv run openclaw-tg <command>` |
| Run tests | `uv run pytest` |
| Run Python script | `uv run python script.py` |
| Add dependency | `uv add <package>` |
| Add dev dependency | `uv add --group dev <package>` |
| Show installed packages | `uv pip list` |

## Troubleshooting

### Missing bot token

```
Failed to load configuration: 1 validation error for TelegramConfig
telegram_bot_token
  Field required
```

**Solution:** Create a `.env` file with `TELEGRAM_BOT_TOKEN=your_token`

### Connection timeout

**Solution:**
- Check your internet connection
- Increase timeout in `.env`: `REQUEST_TIMEOUT=60`
- Try sync mode for debugging: `uv run openclaw-tg --sync test`

### Import errors

**Solution:** Make sure you're using `uv run`:
```bash
# ✅ Correct
uv run openclaw-tg test

# ❌ Wrong (unless venv is activated)
openclaw-tg test
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [.env.example](.env.example) for all configuration options
- Review [tests/](tests/) for usage examples
