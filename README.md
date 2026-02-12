# OpenClaw Telegram Client

A benchmark-ready Telegram client for testing OpenClaw bot performance with dual-mode support (async/sync).

## Features

- **Dual-mode architecture**: Switch between async (performance) and sync (debugging) modes
- **Benchmark framework**: Extensible scenarios for latency, multi-turn conversations, and concurrent sessions
- **Session management**: Track multi-turn conversations with automatic response handling
- **Metrics collection**: Response times, success rates, error tracking
- **CLI interface**: Easy-to-use command-line tools
- **Export results**: JSON and Markdown format support

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a quick reference guide.

## Installation

1. Install dependencies using `uv`:

```bash
cd opencalw-sandbox

# Sync dependencies (creates virtual environment automatically)
uv sync

# Or with dev dependencies
uv sync --group dev
```

2. Set up your environment:

```bash
cp .env.example .env
# Edit .env with your Telegram bot token
```

## Configuration

Create a `.env` file with the following settings:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Optional
OPENCLAW_BOT_USERNAME=openclaw_bot
ASYNC_MODE=true  # true for performance, false for debugging
LOG_LEVEL=INFO
DEBUG_MODE=false
```

## Usage

All commands use `uv run` to execute in the virtual environment:

### Test Connection

```bash
uv run openclaw-tg test
```

### Send a Message

```bash
uv run openclaw-tg send <chat_id> "Hello, OpenClaw!"
```

### List Available Benchmark Scenarios

```bash
uv run openclaw-tg list-scenarios
```

### Run a Benchmark

```bash
# Run scenario 0 (Simple Latency Test)
uv run openclaw-tg benchmark <chat_id> --scenario 0

# Run with output to file
uv run openclaw-tg benchmark <chat_id> --scenario 0 --output results.md
```

### Async/Sync Mode

Override the config file setting with flags:

```bash
# Force async mode (performance)
uv run openclaw-tg --async test

# Force sync mode (debugging)
uv run openclaw-tg --sync test
```

### Verbose Logging

```bash
uv run openclaw-tg -v test
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_telegram_client.py
```

## Architecture

### Core Components

1. **config.py**: Configuration management with Pydantic settings
2. **telegram_client.py**: Telegram Bot API client with dual-mode support
   - `TelegramClient`: Main client class
   - `TelegramSession`: Manages conversation sessions
   - `TelegramMessage`, `TelegramUpdate`: Data models
3. **benchmark_runner.py**: Benchmark framework
   - `BenchmarkRunner`: Executes scenarios and collects metrics
   - `BenchmarkScenario`: Defines test scenarios
   - `BenchmarkMetrics`: Results and statistics
4. **cli.py**: Command-line interface

### Dual-Mode Design

The client supports two execution modes controlled by the `ASYNC_MODE` flag:

**Async Mode (Performance)**
- Uses `aiohttp` for non-blocking I/O
- Supports concurrent sessions
- Optimal for production benchmarks
- Higher throughput

**Sync Mode (Debugging)**
- Uses `requests` for blocking I/O
- Single-threaded execution
- Easier to debug with breakpoints
- Step-through friendly

### Example: Using the Client Directly

```python
import asyncio
from config import load_config
from telegram_client import TelegramClient, TelegramSession

async def main():
    config = load_config()

    async with TelegramClient(config) as client:
        # Get bot info
        bot_info = await client.get_me_async()
        print(f"Connected to: {bot_info['username']}")

        # Create a session
        session = TelegramSession(client, chat_id=123456)

        # Send message and wait for response
        response = await session.send_message_async(
            "Hello, OpenClaw!",
            wait_for_response=True,
            timeout=30.0
        )

        if response:
            print(f"Bot replied: {response.text}")

asyncio.run(main())
```

### Example: Sync Mode

```python
from config import load_config
from telegram_client import TelegramClient, TelegramSession

def main():
    config = load_config()
    config.async_mode = False  # Force sync mode

    with TelegramClient(config) as client:
        bot_info = client.get_me_sync()
        print(f"Connected to: {bot_info['username']}")

        session = TelegramSession(client, chat_id=123456)
        response = session.send_message_sync(
            "Hello, OpenClaw!",
            wait_for_response=True,
            timeout=30.0
        )

        if response:
            print(f"Bot replied: {response.text}")

main()
```

## Benchmark Scenarios

### Pre-defined Scenarios

1. **Simple Latency Test**
   - Type: `LATENCY`
   - Tests: 3 simple queries
   - Purpose: Baseline response time measurement

2. **Multi-turn Conversation**
   - Type: `MULTI_TURN`
   - Tests: 5-message conversation with context
   - Purpose: Session management and context handling

### Creating Custom Scenarios

```python
from benchmark_runner import BenchmarkScenario, BenchmarkType

custom_scenario = BenchmarkScenario(
    name="Custom Test",
    benchmark_type=BenchmarkType.LATENCY,
    messages=["Query 1", "Query 2", "Query 3"],
    num_sessions=1,
    wait_for_response=True,
    response_timeout=30.0,
    inter_message_delay=2.0,
)

runner = BenchmarkRunner(config)
metrics = await runner.run_scenario_async(custom_scenario, chat_id)
```

## Testing

Run tests with uv:

```bash
# All tests
uv run pytest

# Verbose output
uv run pytest -v

# Specific test file
uv run pytest tests/test_telegram_client.py

# With coverage
uv run pytest --cov=. --cov-report=html
```

## Getting a Chat ID

To send messages to the OpenClaw bot, you need a `chat_id`. Here's how to get it:

1. Start a conversation with your bot on Telegram
2. Send any message to the bot
3. Run:

```python
async with TelegramClient(config) as client:
    updates = await client.get_updates_async()
    for update in updates:
        if update.message:
            print(f"Chat ID: {update.message.chat_id}")
```

Or use the CLI:

```bash
uv run python -c "
import asyncio
from config import load_config
from telegram_client import TelegramClient

async def get_chat_id():
    config = load_config()
    async with TelegramClient(config) as client:
        updates = await client.get_updates_async()
        for update in updates:
            if update.message:
                print(f'Chat ID: {update.message.chat_id}')

asyncio.run(get_chat_id())
"
```

## Benchmark Results Format

Results are exported in Markdown format with the following sections:

- Benchmark metadata (timestamp, config)
- Per-scenario metrics:
  - Duration
  - Message counts
  - Success rate
  - Response time statistics (avg, min, max)
  - Error messages

Example output:

```markdown
# Telegram Bot Benchmark Results

**Timestamp:** 2026-02-11 10:30:00
**Async Mode:** true
**Bot Username:** openclaw_bot

## Benchmark 1: latency

- **Duration:** 15.23s
- **Messages Sent:** 3
- **Messages Received:** 3
- **Success Rate:** 100.00%

### Response Times
- **Average:** 4.85s
- **Min:** 4.12s
- **Max:** 5.67s
```

## Troubleshooting

### Connection Errors

- Verify your `TELEGRAM_BOT_TOKEN` is correct
- Check internet connectivity
- Ensure the bot is not blocked

### Timeout Issues

- Increase `REQUEST_TIMEOUT` or `POLLING_TIMEOUT` in `.env`
- Check if the bot is responding (test manually in Telegram)
- Use sync mode for easier debugging

### Debug Mode

Enable detailed logging:

```bash
# In .env
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Or via CLI
uv run openclaw-tg -v --sync test
```

## Project Structure

```
opencalw-sandbox/
├── pyproject.toml          # Project dependencies
├── README.md               # This file
├── .env.example            # Example configuration
├── config.py               # Configuration management
├── telegram_client.py      # Core Telegram client
├── benchmark_runner.py     # Benchmark framework
├── cli.py                  # CLI interface
└── tests/
    ├── conftest.py         # Pytest fixtures
    ├── test_config.py      # Config tests
    └── test_telegram_client.py  # Client tests
```

## Future Enhancements

The benchmark framework is designed to be extensible. Future scenarios could include:

- **Task Completion Accuracy**: Verify correct task execution
- **Load Testing**: Stress test with many concurrent users
- **Latency Distribution**: Percentile analysis (p50, p95, p99)
- **Integration with Sequrity API**: Test through security layer

## License

Part of the Sequrity project.
