# OpenClaw Benchmark Suite

Comprehensive benchmarks for evaluating OpenClaw bot capabilities across file manipulation, web research, calendar management, and email handling.

## Overview

The benchmark suite tests **accuracy** and **latency** of OpenClaw agents across real-world use cases. Each scenario includes:

- **Pre-checks**: Verify agent configuration before testing
- **Setup**: Prepare test environment (create files, send emails, etc.)
- **Tasks**: 3 progressive tasks per scenario
- **Validation**: Automatic accuracy scoring (0-100%)
- **Cleanup**: Remove test data after completion

## Available Scenarios

### 1. File Manipulation (`file`)

Tests agent's ability to create, read, transform, and extract data from files.

**Required Skills**: `file_system_access`, `text_processing`, `data_transformation`

**Tasks**:
1. **File Creation** (Low difficulty, 20s timeout)
   - Create `summary.md` with bullet list of 3 programming languages
   - Validation: Checks for markdown format and all 3 items

2. **JSON to CSV Transformation** (Medium difficulty, 30s timeout)
   - Read `data.json` and create CSV with names and emails
   - Validation: Correct columns, matching records, proper CSV format

3. **Text Extraction** (Medium difficulty, 25s timeout)
   - Extract action items from meeting notes
   - Validation: Correct action items, excludes non-action text

**Setup**: Creates test workspace at `/tmp/openclaw_benchmark/` with:
- `data.json`: Sample user records
- `notes.txt`: Meeting notes with action items
- `reports/`: Empty directory for outputs

### 2. Web Research (`web`)

Tests agent's ability to browse web pages, extract information, and cite sources.

**Required Skills**: `web_browsing`, `information_extraction`, `research`

**Tasks**:
1. **Factual Extraction** (Low difficulty, 40s timeout)
   - Extract Python's creation year and creator from Wikipedia
   - Validation: Contains founding date (1991) and creator info

2. **Repository Analysis** (Medium difficulty, 50s timeout)
   - Analyze GitHub repository and describe its purpose
   - Validation: Identifies repo, describes purpose, includes metadata

3. **Multi-Source Research** (Medium difficulty, 60s timeout)
   - Research "OpenClaw features" and provide 3 capabilities with sources
   - Validation: 3 distinct capabilities, 3 source URLs

**Setup**: Prepares test URLs:
- Wikipedia: Python programming language article
- GitHub: awesome-openclaw-usecases repository
- Topic: OpenClaw AI agent features

### 3. Calendar Management (`calendar`) [Coming Soon]

Tests agent's ability to create events, detect conflicts, and summarize schedules.

### 4. Email Handling (`email`) [Coming Soon]

Tests agent's ability to read, classify, and draft email responses.

## Usage

### Run All Scenarios

```bash
# Async mode (recommended for production)
uv run openclaw-tg benchmark-suite <chat_id> --scenario all

# Sync mode (better for debugging)
uv run openclaw-tg --sync benchmark-suite <chat_id> --scenario all
```

### Run Specific Scenario

```bash
# File manipulation only
uv run openclaw-tg benchmark-suite <chat_id> --scenario file

# Web research only
uv run openclaw-tg benchmark-suite <chat_id> --scenario web
```

### Skip Setup Phase

```bash
# Use existing test data (for repeated runs)
uv run openclaw-tg benchmark-suite <chat_id> --scenario file --no-setup
```

### Export Results

```bash
# Save results to JSON file
uv run openclaw-tg benchmark-suite <chat_id> --scenario all --output results.json
```

### Verbose Logging

```bash
# Enable detailed logging for debugging
uv run openclaw-tg -v benchmark-suite <chat_id> --scenario file
```

## Getting Started

### 1. Set Up Your Bot

Make sure your `.env` file is configured:

```bash
TELEGRAM_BOT_TOKEN=your_token_here
OPENCLAW_BOT_USERNAME=your_bot_username
ASYNC_MODE=true
```

### 2. Get Your Chat ID

Start a conversation with your bot on Telegram, then:

```bash
uv run python -c "
import asyncio
from config import load_config
from telegram_client import TelegramClient

async def main():
    config = load_config()
    config.async_mode = True
    async with TelegramClient(config) as client:
        updates = await client.get_updates_async()
        for update in updates:
            if update.message:
                print(f'Chat ID: {update.message.chat_id}')

asyncio.run(main())
"
```

### 3. Configure Your Agent

Ensure your OpenClaw bot has the required skills for each scenario:

**For File Scenario:**
- File system access enabled
- Write permissions to `/tmp/`

**For Web Scenario:**
- Web browsing skill installed
- Internet connectivity

### 4. Run Benchmarks

```bash
# Start with file scenario (simplest)
uv run openclaw-tg benchmark-suite <your_chat_id> --scenario file

# Then try web research
uv run openclaw-tg benchmark-suite <your_chat_id> --scenario web

# Finally run all scenarios
uv run openclaw-tg benchmark-suite <your_chat_id> --scenario all --output full_results.json
```

## Understanding Results

### Console Output

```
============================================================
OpenClaw Benchmark Suite
Running 2 scenario(s): File Manipulation, Web Research
Mode: Async
Skip setup: False
============================================================

[1/2] Running scenario: File Manipulation
Description: Tests agent's ability to create, read, transform, and extract data from files
Required skills: file_system_access, text_processing, data_transformation

Running health checks...
Running setup...
Running task 1/3: File Creation
Task completed: success=True, accuracy=100.0, latency=15.23s
...

------------------------------------------------------------
Scenario: File Manipulation
Duration: 78.45s
Tasks passed: 3/3
Average accuracy: 95.7%
Average latency: 23.15s
------------------------------------------------------------
```

### JSON Export Format

```json
{
  "config": {
    "async_mode": true,
    "openclaw_bot_username": "your_bot"
  },
  "scenarios": [
    {
      "scenario_name": "File Manipulation",
      "total_duration": 78.45,
      "all_tasks_passed": true,
      "average_accuracy": 95.7,
      "average_latency": 23.15,
      "task_results": [
        {
          "task_name": "File Creation",
          "success": true,
          "latency": 15.23,
          "accuracy_score": 100.0,
          "validation_details": {...}
        }
      ]
    }
  ],
  "summary": {
    "total_scenarios": 2,
    "total_tasks": 6,
    "tasks_passed": 5,
    "overall_accuracy": 87.3
  }
}
```

## Metrics

### Accuracy Score (0-100%)

Each task receives an accuracy score based on:
- **Correctness**: Did the agent produce the right output?
- **Completeness**: Are all required elements present?
- **Format**: Is the output in the expected format?

**Scoring Guidelines**:
- **90-100%**: Excellent - All requirements met
- **70-89%**: Good - Minor issues or missing elements
- **50-69%**: Fair - Significant gaps in output
- **0-49%**: Poor - Major errors or incomplete

### Latency (seconds)

Time from sending prompt to receiving complete response.

**Target Latencies**:
- Simple tasks (file creation): < 20s
- Medium tasks (data transformation): < 30s
- Complex tasks (multi-source research): < 60s

### Success Rate

Binary pass/fail based on minimum accuracy threshold (typically 70%).

## Troubleshooting

### "No response from bot or timeout"

**Causes**:
- Bot is not responding
- Task timeout too short
- Bot lacks required skills

**Solutions**:
- Test bot connection: `uv run openclaw-tg test`
- Increase timeouts in scenario code
- Verify required skills are installed
- Use sync mode for debugging: `--sync`

### "Validation error" or Low Accuracy Scores

**Causes**:
- Bot output doesn't match expected format
- Bot misunderstood the task
- Validation logic too strict

**Solutions**:
- Review `validation_details` in JSON output
- Check bot's actual response text
- Adjust validation criteria if needed
- Use verbose logging: `-v`

### "Setup failed"

**Causes**:
- Insufficient permissions
- Missing directories
- Network issues (for web scenario)

**Solutions**:
- Check file permissions for `/tmp/`
- Verify internet connectivity
- Review setup logs with `-v`

### File Scenario Failures

**Common Issues**:
- Bot can't access `/tmp/openclaw_benchmark/`
- Bot doesn't understand markdown format
- Bot includes extra content beyond requirements

**Debug**:
```bash
# Check workspace manually
ls -la /tmp/openclaw_benchmark/

# Run with verbose logging
uv run openclaw-tg -v --sync benchmark-suite <chat_id> --scenario file
```

### Web Scenario Failures

**Common Issues**:
- Web browsing skill not installed
- Bot can't access URLs
- Bot doesn't extract correct information

**Debug**:
- Verify URLs are accessible: `curl -I https://en.wikipedia.org/...`
- Check bot has web browsing capability
- Review actual bot response in validation details

## Extending Benchmarks

### Creating Custom Scenarios

1. **Define Scenario Class**:

```python
from benchmarks.base import ScenarioBase, BenchmarkTask

class MyScenario(ScenarioBase):
    def __init__(self):
        super().__init__(
            name="My Custom Scenario",
            description="Tests custom capability",
            required_skills=["skill1", "skill2"]
        )
        self._define_tasks()

    def _define_tasks(self):
        self.add_task(BenchmarkTask(
            name="Task 1",
            prompt="Do something",
            expected_output_description="Expected result",
            validation_fn=self.validator.validate_task1,
            timeout=30.0
        ))

    def pre_check(self):
        # Return list of HealthCheckResult
        pass

    def setup(self):
        # Return SetupResult
        pass

    def cleanup(self):
        # Return bool
        pass
```

2. **Create Validator**:

```python
from benchmarks.base import TaskResult

class MyValidator:
    @staticmethod
    def validate_task1(response: str, setup_data: dict) -> TaskResult:
        # Check response and assign accuracy score
        return TaskResult(
            task_name="Task 1",
            prompt="...",
            success=True,
            latency=0.0,
            accuracy_score=95.0,
            response_text=response
        )
```

3. **Add to CLI**:

Update `cli.py` to import and include your scenario:

```python
from benchmarks.scenarios import FileScenario, WebScenario, MyScenario

# In run_benchmark_suite_async:
if args.scenario == "my":
    scenarios.append(MyScenario())
```

## Best Practices

### For Agent Testing

1. **Start Simple**: Run file scenario first (no external dependencies)
2. **Iterate**: Run benchmarks after agent configuration changes
3. **Compare**: Track accuracy over time to measure improvements
4. **Debug**: Use sync mode (`--sync`) and verbose logging (`-v`) for failures

### For Benchmark Development

1. **Clear Prompts**: Make task instructions unambiguous
2. **Flexible Validation**: Allow for reasonable variations in output
3. **Incremental Difficulty**: Order tasks from easy to hard
4. **Real-World Tasks**: Base scenarios on actual use cases

### For Performance Analysis

1. **Consistent Environment**: Use same bot configuration for comparisons
2. **Multiple Runs**: Average results over 3-5 runs for reliability
3. **Export Data**: Save JSON results for long-term tracking
4. **Identify Patterns**: Look for consistent failure points

## Architecture

```
benchmarks/
├── base.py                 # Core classes (ScenarioBase, TaskResult, etc.)
├── scenarios/
│   ├── file_scenario.py    # File manipulation tests
│   └── web_scenario.py     # Web research tests
├── setup/
│   ├── file_setup.py       # Create test files
│   └── web_setup.py        # Prepare test URLs
└── validators/
    ├── file_validator.py   # Validate file tasks
    └── web_validator.py    # Validate web tasks
```

## Roadmap

- [x] File manipulation scenario
- [x] Web research scenario
- [ ] Calendar management scenario
- [ ] Email handling scenario
- [ ] Accuracy percentile analysis (p50, p95, p99)
- [ ] Automated regression testing in CI
- [ ] Benchmark result visualization dashboard
- [ ] Multi-agent collaboration scenarios

## Contributing

To add new benchmark scenarios:

1. Create scenario class in `benchmarks/scenarios/`
2. Create setup utilities in `benchmarks/setup/`
3. Create validators in `benchmarks/validators/`
4. Update CLI to include new scenario
5. Document tasks and validation criteria
6. Add tests for validation logic

## Related Documentation

- [README.md](README.md) - Main project documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [.env.example](.env.example) - Configuration options

## License

Part of the Sequrity project.
