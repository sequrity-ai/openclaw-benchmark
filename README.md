# OpenClaw Benchmark Client

A benchmarking framework for testing OpenClaw bot performance. Supports two execution modes:

- **Multi-turn mode** (default): An AI agent (powered by OpenAI) simulates a real user, conducting natural conversations with the bot to accomplish tasks.
- **Single-turn mode** (`--single-turn`): Each task prompt is sent directly to the bot — no AI agent, no conversation, just prompt → response → validate.

## How It Works

### Multi-turn mode (default)

1. An **AI agent** (powered by OpenAI) receives a task description
2. The agent sends messages to the **OpenClaw bot** (via Telegram or local CLI)
3. The agent and bot exchange messages until the task is complete (up to 10 turns, configurable via `--max-turns`)
4. A **validator** checks whether the task was actually completed correctly
5. Results are collected: turns taken, latency, success/fail, accuracy score

### Single-turn mode (`--single-turn`)

1. The task **prompt is sent directly** to the bot (no AI agent involved)
2. The bot's response is captured
3. A **validator** checks the response
4. Results are collected: latency, success/fail, accuracy score, token usage

Single-turn mode is faster, cheaper (no OpenAI API cost), and removes the AI agent as a confounding variable.

---

## Two Modes

The framework supports two operating modes. Choose based on what you are testing.

### Telegram Mode (default)

The benchmark acts as a real Telegram user and messages your deployed OpenClaw bot. This tests the full production stack including Telegram round-trips.

- Uses Pyrogram user-based client (your personal account, not a bot token)
- Requires one-time Telegram authentication (`just auth`)
- Requires SSH credentials to the bot server for file-based validation
- Slower due to network latency (~30s per bot response)

**Use this when:** testing a real deployed bot, running sweeps across all models, or doing production-level validation.

### Local Mode

The benchmark calls `openclaw agent` directly as a subprocess. No Telegram involved.

- Calls the local OpenClaw CLI: `openclaw agent --message "..." --json`
- No Telegram auth required
- Full filesystem access — validators can inspect created files directly
- Much faster (~2-5s per response)

**Use this when:** developing new scenarios, rapid iteration, or running quick smoke tests.

---

## Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager
- An OpenAI API key (required for multi-turn mode; **not needed** for `--single-turn`)
- For Telegram mode: credentials from [my.telegram.org](https://my.telegram.org) and SSH access to the bot server
- For local mode: `openclaw` CLI installed and on `$PATH`

---

## Installation

```bash
# Clone and enter the project
cd opencalw-sandbox

# Install dependencies (creates .venv automatically)
uv sync

# Copy and fill in your config
cp .env.example .env
```

---

## Configuration

All configuration lives in `.env`. Here is what you need depending on what you want to run.

### Always Required (multi-turn mode)

```bash
# AI agent that simulates the user in conversations
# NOT required when using --single-turn mode
OPENAI_API_KEY=sk-proj-...
AI_AGENT_MODEL=gpt-5-mini
```

### Telegram Mode

```bash
LOCAL_MODE=false

# Get these from https://my.telegram.org → API development tools
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+1234567890        # Your personal phone number with country code

# The bot's username (without @)
OPENCLAW_BOT_USERNAME=your_openclaw_bot

# SSH access to the bot server (required for file/summarize validation)
BOT_SSH_HOST=your-bot-server.example.com
BOT_SSH_PORT=22
BOT_SSH_USER=ubuntu
BOT_SSH_KEY_PATH=~/.ssh/id_rsa
BOT_WORKSPACE_PATH=/tmp/openclaw_benchmark
```

### Local Mode

```bash
LOCAL_MODE=true
AGENT_ID=main    # The openclaw agent name (default: main)
```

### Optional Performance Tuning

```bash
ASYNC_MODE=true               # true = async (faster, default); false = sync (easier to debug)
MAX_CONVERSATION_TURNS=10     # Max turns per task before giving up (overridable via --max-turns)
CONVERSATION_TIMEOUT=300.0    # Seconds per task before timeout
TIMEOUT_MULTIPLIER=1.0        # Scale all timeouts (use >1 on slow machines)
```

### Scenario-Specific Config

Only needed if you run those specific scenarios.

```bash
# Web search scenario
TAVILY_API_KEY=tvly-...

# Gmail scenario — requires TWO Gmail accounts
# Account 1: the bot's Gmail (configured in OpenClaw via clawhub install gog)
# Account 2: a separate benchmark account for sending test emails and validating
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...
GMAIL_BENCHMARK_EMAIL=benchmark@gmail.com   # Account 2 (with OAuth2 credentials)
GMAIL_BOT_EMAIL=bot@gmail.com               # Account 1 (bot's account)

# GitHub scenario — requires TWO GitHub accounts
# Account 1: the bot's GitHub (configured in OpenClaw via clawhub install steipete/github)
# Account 2: a separate benchmark account with a test repo
GITHUB_TOKEN=ghp_...                        # PAT for account 2, "repo" scope
GITHUB_TEST_REPO_OWNER=your-github-username
GITHUB_TEST_REPO_NAME=openclaw-benchmark-test
```

### Logging

```bash
LOG_LEVEL=INFO      # DEBUG | INFO | WARNING | ERROR
DEBUG_MODE=false    # true = very verbose output
```

---

## Quick Start

### Local Mode (fastest, no auth needed)

```bash
# Run a single scenario (multi-turn, requires OPENAI_API_KEY)
just bench file mode=local
just bench weather mode=local
just bench web mode=local

# Single-turn mode (no OPENAI_API_KEY needed)
uv run python cli.py --local benchmark-suite --scenario file --single-turn

# Single-turn, easy tasks only
uv run python cli.py --local benchmark-suite --single-turn --difficulty easy

# Run all scenarios
just bench all mode=local

# Run a sweep across all configured models
just sweep mode=local
```

### Telegram Mode

```bash
# One-time: authenticate with Telegram
just auth

# Run a single scenario
just bench file
just bench weather
just bench all

# Run sweep across all available models on the remote bot
just sweep
just sweep output=sweep_results.json
```

---

## All Commands

### Running Benchmarks

```bash
# Single scenario, Telegram mode (default)
just bench file
just bench weather
just bench web
just bench summarize
just bench gmail
just bench github
just bench compound

# Single scenario, local mode
just bench file mode=local
just bench all mode=local

# Switch the bot's model before running
just bench file model="anthropic/claude-opus-4-5"

# Save results to JSON
just bench file output=results.json
just bench all mode=local output=results.json

# Single-turn mode (no AI agent, no OPENAI_API_KEY needed)
uv run python cli.py --local benchmark-suite --single-turn --scenario file
uv run python cli.py --local benchmark-suite --single-turn --scenario all -o results_single.json

# Filter by task difficulty (easy/medium/hard)
uv run python cli.py --local benchmark-suite --difficulty easy
uv run python cli.py --local benchmark-suite --single-turn --difficulty easy

# Override max conversation turns (multi-turn mode only)
uv run python cli.py --local benchmark-suite --max-turns 5
uv run python cli.py --local benchmark-suite --max-turns 3 --difficulty easy
```

The `bench` recipe signature:
```
just bench <scenario> [mode=telegram|local] [model=provider/model] [output=file.json]
```

#### CLI flags reference

| Flag | Description |
|------|-------------|
| `--single-turn` | Send prompts directly to bot, skip AI agent (no OPENAI_API_KEY needed) |
| `--difficulty <level>` | Only run tasks of this difficulty: `easy`, `medium`, `hard`, or `all` (default: `all`) |
| `--max-turns <n>` | Override max conversation turns per task (default: from `MAX_CONVERSATION_TURNS` env) |
| `--scenario <name>` | Run a specific scenario or `all` |
| `--bot-model <model>` | Switch bot model before running |
| `-o <path>` | Export results to JSON |
| `--no-setup` | Skip setup phase |
| `--skip-missing` / `--no-skip-missing` | Skip or fail on scenarios with missing skills |

Logs are automatically saved to `logs/bench_<scenario>_<timestamp>.log`.

### Model Sweep

Discovers all models configured on the bot, runs every scenario against each, and prints a cross-model summary table.

```bash
# Telegram mode (discovers models via SSH)
just sweep
just sweep output=sweep_results.json

# Local mode (discovers models via 'openclaw models list --json')
just sweep mode=local
just sweep mode=local output=sweep_results.json
```

The `sweep` recipe signature:
```
just sweep [mode=telegram|local] [output=file.json]
```

### Evaluating Results

```bash
just evaluate sweep_results.json
```

### Authentication (Telegram Mode Only)

```bash
just auth         # Authenticate and save session
just auth-reset   # Delete saved session (re-authenticate next time)
```

### Viewing Logs

```bash
just logs         # List the 20 most recent log files
```

### Development

```bash
just install          # Install runtime dependencies
just install-dev      # Install with dev/test dependencies

just test             # Run pytest
just test-cov         # Run tests with HTML coverage report
just lint             # Check code with ruff
just format           # Auto-format with ruff
just format-check     # Check formatting without modifying files
just dev              # format + lint + test
just ci               # format-check + lint + test-cov
```

### Cleanup

```bash
just clean            # Remove test artifacts, .pyc, coverage
just clean-logs       # Remove logs/ directory
just clean-workspace  # Remove /tmp/openclaw_benchmark (local workspace)
just clean-all        # Everything above + .venv + uv.lock
```

---

## Scenarios

Each scenario has 9 tasks (3 easy, 3 medium, 3 hard). Required skills must be installed on the bot before running.

| Scenario | Required Skill | What It Tests |
|---|---|---|
| `file` | None (core tools) | File creation, JSON→CSV, data extraction, log analysis, config diffs |
| `weather` | `clawhub install steipete/weather` | Current weather, forecasts, multi-city comparisons |
| `web` | `clawhub install steipete/tavily` | Web search, fact retrieval, research questions |
| `summarize` | `clawhub install steipete/summarize` | URL summaries, YouTube summaries, document comparison |
| `gmail` | `clawhub install gog` | Send email, read inbox, search, thread replies |
| `github` | `clawhub install steipete/github` | Create issues, list issues, read repo files, create PRs |
| `compound` | weather + tavily + github + summarize | Multi-skill chains: weather+issue, web+summarize, 3-step chains |
| `all` | All of the above | Runs all 7 scenarios sequentially |

### Installing Skills on the Bot

Before running scenarios that need skills, install them on your OpenClaw bot:

```bash
clawhub install steipete/weather
clawhub install steipete/tavily
clawhub install steipete/summarize
clawhub install steipete/github
clawhub install gog
```

The benchmark will warn you if a required skill is missing and skip the scenario.

---

## Custom Bot Prompt

You can inject a custom system prompt into the bot before running benchmarks. This replaces the bot's `SOUL.md` for the duration of the run and restores the original automatically when done.

### Setup

1. Create a prompt file (plain text or markdown):

```bash
cat > my_prompt.md << 'EOF'
You are a helpful assistant that always responds concisely.
Never use markdown formatting. Keep answers under 100 words.
EOF
```

2. Set the environment variables in `.env`:

```bash
CUSTOM_BOT_PROMPT_FILE=./my_prompt.md          # Path to your prompt file
BOT_WORKSPACE_DIR=~/.openclaw/workspace         # Where SOUL.md lives (default)
```

3. Run the benchmark normally — the prompt is injected automatically:

```bash
uv run python cli.py --local benchmark-suite --scenario file -o results.json
```

### What Happens

- **Before** the benchmark: your prompt file replaces `SOUL.md` in the bot workspace. The original is backed up to `SOUL.md.benchmark_backup`.
- **After** the benchmark (or on error): the original `SOUL.md` is restored automatically.
- If no `SOUL.md` existed before, the injected one is removed.
- Leave `CUSTOM_BOT_PROMPT_FILE` empty (or unset) to run with the bot's default prompt.

### Use Cases

- Compare how different system prompts affect task accuracy
- Test prompt robustness across scenarios
- A/B test prompt variations with `--bot-model` held constant

---

## Interpreting Results

### Output Locations

| Location | What | When |
|----------|------|------|
| **Console** | Live progress: task pass/fail, scenario summaries | During run |
| **`-o results.json`** | Full structured results with per-task details | After run completes |
| **`logs/bench_<scenario>_<timestamp>.log`** | Verbose log: every AI agent turn, bot response, validation details, token counts | After run (auto-created) |

### Result JSON Structure

```bash
# Quick summary from any result file
python3 -c "
import json, sys
with open(sys.argv[1]) as f: data = json.load(f)
for s in data['scenarios']:
    passed = sum(1 for t in s['task_results'] if t['success'])
    total = len(s['task_results'])
    acc = sum(t['accuracy_score'] for t in s['task_results']) / total if total else 0
    tok_in = sum(t.get('input_tokens', 0) for t in s['task_results'])
    tok_out = sum(t.get('output_tokens', 0) for t in s['task_results'])
    print(f'{s[\"scenario_name\"]:20s}: {passed}/{total} ({acc:5.1f}%)  tokens: {tok_in:,} in / {tok_out:,} out')
" results.json
```

The JSON contains:

```
results.json
├── config                          # Run settings (mode, model, async, single_turn/multi_turn)
└── scenarios[]
    ├── scenario_name               # "File Manipulation", "Gmail Email", etc.
    ├── total_duration              # Wall-clock time for the scenario (seconds)
    ├── health_checks[]             # Pre-flight checks (skills, API keys, workspace)
    ├── setup_result                # Whether seed data was created successfully
    └── task_results[]
        ├── task_name               # "File Organization", "Email Search", etc.
        ├── success                 # true/false — did the task pass validation?
        ├── accuracy_score          # 100.0 (pass) or 0.0 (fail) — binary scoring
        ├── latency                 # Seconds from first message to last response
        ├── completion_reason       # "goal_achieved" | "max_turns" | "timeout" | "error" | "single_turn"
        ├── conversation_turns      # Number of AI↔bot exchanges
        ├── conversation_history[]  # Full transcript: {turn, user, bot, timestamp}
        ├── validation_details      # Scenario-specific: what was checked and what failed
        ├── input_tokens            # Total input tokens consumed by the bot
        ├── output_tokens           # Total output tokens generated by the bot
        ├── reasoning_tokens        # Reasoning/chain-of-thought tokens (if applicable)
        └── cache_read_tokens       # Prompt-cache hits
```

### Scoring

All tasks use **binary scoring**: 100% (pass) or 0% (fail). There is no partial credit.

Validation is **fully deterministic** — no LLM-as-judge. Each validator checks concrete outputs:

| Scenario | What's Validated |
|----------|-----------------|
| File | Files exist on disk with correct content (CSV rows, JSON keys, directory structure) |
| Weather | Bot response contains temperature numbers within ±3°C of Open-Meteo API ground truth |
| Gmail | Emails found/sent via Gmail API, correct recipients, subjects, labels |
| GitHub | Issues/PRs exist via GitHub API, correct titles, labels, content |
| Summarize | Response contains required keywords and structural elements |
| Web Search | Response contains factual keywords verified against known answers |
| Compound | Multi-skill chain: each step validated independently |

### Reading the Logs

Logs are saved to `logs/` automatically. Key patterns to grep for:

```bash
# See all task results at a glance
grep "Task completed:" logs/bench_all_*.log

# See full AI agent ↔ bot conversation for a specific task
grep -A 5 "TURN.*REQUEST\|TURN.*RESPONSE" logs/bench_file_*.log

# See what validation checked and why it failed
grep "Validation details:" logs/bench_all_*.log

# See token usage per turn
grep "Token usage:" logs/bench_all_*.log

# See errors and timeouts
grep -E "ERROR|timeout|FAIL" logs/bench_all_*.log
```

### Comparing Models

Run the same benchmark across models and compare:

```bash
# Multi-turn comparison
uv run python cli.py --local benchmark-suite --scenario all --bot-model "openai/gpt-5.2" -o results_gpt52.json
uv run python cli.py --local benchmark-suite --scenario all --bot-model "openai/gpt-5-mini" -o results_mini.json

# Single-turn comparison (faster, no AI agent cost)
uv run python cli.py --local benchmark-suite --single-turn --scenario all --bot-model "openai/gpt-5.2" -o results_gpt52_single.json
uv run python cli.py --local benchmark-suite --single-turn --scenario all --bot-model "openai/gpt-5-mini" -o results_mini_single.json

# Analyze results with the leaderboard script (shows mode column)
python3 scripts/analyze_logs.py results_gpt52.json results_mini.json results_gpt52_single.json results_mini_single.json
```

---

## Validation

The framework uses a two-phase validation approach:

**Phase 1 — Conversation detection:** The AI agent looks for completion signals in the conversation (e.g. "thanks", "done", the bot says "task complete"). Marks the conversation as `goal_achieved`, `max_turns`, `timeout`, or `error`.

**Phase 2 — Result validation:** A scenario-specific validator checks the actual output:

| Mode | Validation |
|---|---|
| Local | Full automated validation — validators inspect the local filesystem directly |
| Telegram | SSH-based validation — validators download files from the bot server via SSH and inspect them locally |

For Telegram mode, SSH credentials (`BOT_SSH_*`) must be configured. Without them, file-based scenarios (file, summarize) can only do conversation-level validation.

**Reading results:**
- `success: true` + `accuracy: 100%` — task completed and validated
- `success: false` + `accuracy: 0%` — task failed or validation failed
- `completion_reason: single_turn` — single-turn mode (one prompt, one response)
- `completion_reason: timeout` — bot did not respond within the timeout
- `completion_reason: max_turns` — task not finished within max turns

---

## Project Structure

```
opencalw-sandbox/
├── cli.py                      # Entry point: benchmark-suite, benchmark-sweep
├── config.py                   # Pydantic settings from .env
├── telegram_client.py          # Pyrogram user-based Telegram client
├── local_client.py             # Local openclaw CLI subprocess wrapper
├── telegram_auth.py            # One-time Telegram auth helper
├── justfile                    # Task runner (use 'just' to see all commands)
├── .env.example                # Annotated config template
│
├── benchmarks/
│   ├── base.py                 # ScenarioBase, TaskResult, BenchmarkTask
│   ├── ai_agent.py             # BenchmarkAgent — OpenAI-powered user simulator
│   ├── security.py             # SecretScanner — detects leaked API keys in outputs
│   ├── skill_checker.py        # Detects which skills are available on the bot
│   ├── remote_workspace.py     # SSH workspace setup + RemoteWorkspaceManager
│   │                           # + LocalModelManager (for local sweep)
│   ├── scenarios/
│   │   ├── file_scenario.py
│   │   ├── weather_scenario.py
│   │   ├── web_scenario.py
│   │   ├── summarize_scenario.py
│   │   ├── gmail_scenario.py
│   │   ├── github_scenario.py
│   │   └── compound_scenario.py
│   ├── setup/
│   │   ├── file_setup.py       # Creates seed files in workspace
│   │   ├── gmail_setup.py      # Gmail API helper (sends test emails)
│   │   ├── github_setup.py     # GitHub API helper (seeds test issues)
│   │   └── summarize_setup.py  # Uploads documents to workspace
│   └── validators/
│       ├── file_validator.py
│       ├── web_validator.py
│       ├── weather_validator.py
│       ├── summarize_validator.py
│       ├── gmail_validator.py
│       ├── github_validator.py
│       └── compound_validator.py
│
├── tools/
│   └── get_gmail_token.py      # Generate Gmail OAuth2 refresh token
│
└── tests/
    ├── conftest.py
    └── test_*.py
```

---

## Troubleshooting

**`openclaw CLI not found`** (local mode)
Install OpenClaw and make sure it is on your `$PATH`. Run `openclaw --version` to verify.

**`OPENAI_API_KEY is required`**
Set `OPENAI_API_KEY` in your `.env`. The AI agent that drives multi-turn conversations requires it. Alternatively, use `--single-turn` mode which doesn't need an OpenAI API key.

**`benchmark-sweep requires SSH credentials`** (Telegram mode sweep)
Set `BOT_SSH_HOST`, `BOT_SSH_USER`, and either `BOT_SSH_KEY_PATH` or `BOT_SSH_PASSWORD` in `.env`. The sweep needs SSH to discover and switch models on the remote bot.

**`No models found`** (local mode sweep)
Make sure `openclaw models list --json` returns output in your terminal. The sweep calls this to discover models.

**Scenario skipped with "missing skills"**
Install the required skill on your bot (see the scenario table above), then re-run.

**Telegram auth loop / session errors**
Delete the session file and re-authenticate:
```bash
just auth-reset
just auth
```

**Bot goes silent / response timeout after 30s**
Some compound tasks involving the Summarize skill can cause the bot to process silently without sending a Telegram reply. This is a bot-side issue — the benchmark logs `Response timeout after 30.0s`. The task is marked failed. This is expected behavior to measure.

**Results always 0% accuracy in Telegram mode**
Configure SSH credentials in `.env` so the framework can download and validate files from the bot server.

**Enable debug logging**
```bash
# In .env:
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Or inline:
uv run python cli.py -v --async benchmark-suite --scenario file
```

---

## Gmail Setup (detailed)

The Gmail scenario requires two Gmail accounts because the bot sends/reads from one account, and the benchmark validates from a separate account.

1. Create a **benchmark Gmail account** (separate from the bot's account)
2. Go to [Google Cloud Console](https://console.cloud.google.com/)
3. Create a project → Enable the Gmail API
4. Create OAuth2 credentials (Desktop app type) for the benchmark account
5. Generate a refresh token:
   ```bash
   uv run python tools/get_gmail_token.py
   ```
6. Copy the credentials into `.env` (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`)
7. Set `GMAIL_BENCHMARK_EMAIL` (the benchmark account) and `GMAIL_BOT_EMAIL` (the bot's account)

---

## GitHub Setup (detailed)

1. Create a **benchmark GitHub account** (separate from the bot's account)
2. Create a test repository in that account
3. Generate a Personal Access Token with `repo` scope: [github.com/settings/tokens](https://github.com/settings/tokens)
4. Set `GITHUB_TOKEN`, `GITHUB_TEST_REPO_OWNER`, and `GITHUB_TEST_REPO_NAME` in `.env`

---

## License

Part of the Sequrity project.
