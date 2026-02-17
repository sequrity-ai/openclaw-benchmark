# OpenClaw Benchmark Suite

Comprehensive benchmarks for evaluating OpenClaw bot capabilities across file manipulation, web research, weather, email, content summarization, GitHub operations, and multi-skill compound tasks.

## Overview

The benchmark suite tests **accuracy** and **latency** of OpenClaw agents across real-world use cases. Each scenario includes:

- **Pre-checks**: Verify agent configuration and required skills before testing
- **Setup**: Prepare test environment (create files, seed data, send emails, etc.)
- **Tasks**: 9 progressive tasks per scenario (Easy → Medium → Hard)
- **Validation**: Automatic accuracy scoring (0% or 100% per task)
- **Cleanup**: Remove all test data after completion

## Running Benchmarks

```bash
# Run all scenarios
just bench all

# Run a single scenario
just bench file
just bench weather
just bench web
just bench summarize
just bench gmail
just bench github
just bench compound

# Save results to JSON
just bench all output=results.json
```

## Available Scenarios

### 1. File Manipulation (`file`)

Tests the agent's ability to create, read, transform, and extract data from files on the remote workspace.

**Required Skills**: None (built-in file system tools)

**Setup**: Creates test workspace at `/tmp/openclaw_benchmark/` with structured data files including JSON, CSV, XML, log files, and configuration files.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | File Organization | Easy | Create user directories and profile.txt files from data.json |
| 2 | File Modification | Easy | Count action items from notes and update profile.txt files |
| 3 | File Consolidation | Easy | Aggregate profile data into users_summary.csv |
| 4 | Recursive File Search | Medium | Find all .log files and create log_summary.txt |
| 5 | Data Transformation | Medium | Transform sales_data.csv to sales_report.json with aggregations |
| 6 | File Comparison | Medium | Compare config_v1.ini and config_v2.ini, create config_diff.txt |
| 7 | Multi-Step Data Pipeline | Hard | Merge employees.csv, departments.json, and projects.xml into department_report.json |
| 8 | Advanced Log Analysis | Hard | Parse application.log and generate log_analysis.json with error statistics |
| 9 | Data Validation Report | Hard | Validate inventory.csv data quality and create validation_report.json |

---

### 2. Weather (`weather`)

Tests the agent's ability to retrieve, interpret, and reason about weather data.

**Required Skills**: `steipete/weather`

**Setup**: No special setup required.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | Current Weather | Easy | What's the current weather in San Francisco? |
| 2 | Weather Forecast | Easy | Get the weather forecast for New York for the next 3 days |
| 3 | Weather Comparison | Easy | Compare current weather in London vs Tokyo — which is warmer? |
| 4 | Multi-City Weather | Medium | Tell me the current weather in Paris, Berlin, and Rome |
| 5 | Weather Alerts | Medium | Are there any weather alerts or warnings for Miami? |
| 6 | Temperature Trend | Medium | What's the temperature trend for Seattle over the next week? |
| 7 | Travel Weather Planning | Hard | I'm planning a trip to Barcelona next week — what should I pack? |
| 8 | Best Weather Day | Hard | Which of the next 5 days in Chicago is best for outdoor activities? |
| 9 | Severe Weather Risk | Hard | Is there any risk of severe weather in Houston this weekend? |

---

### 3. Web Search (`web`)

Tests the agent's ability to search the web, extract information, and synthesize results.

**Required Skills**: `tavily-search`

**Setup**: No special setup required.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | Factual Web Search | Easy | When was Python created and who created it? |
| 2 | Comparison Research | Easy | Compare Python vs JavaScript — give 3 key differences |
| 3 | Current Events Research | Easy | Find recent developments in artificial intelligence |
| 4 | Multi-Query Search | Medium | Search for both 'Python async programming' and 'FastAPI tutorials' |
| 5 | Domain-Specific Search | Medium | Find recent articles about AI on techcrunch.com |
| 6 | News Search | Medium | What are the latest news about climate change? |
| 7 | Time-Filtered Search | Hard | Find articles about OpenAI published in the last week |
| 8 | Search Comparison | Hard | Search for 'React' vs 'Vue' and tell me which has more results |
| 9 | Topic Analysis | Hard | Search for 'machine learning' and summarize the main topics |

---

### 4. Summarize (`summarize`)

Tests the agent's ability to read and summarize URLs, YouTube videos, and local documents.

**Required Skills**: `steipete/summarize`

**Setup**: Creates local documents at `/tmp/openclaw_benchmark/documents/` including business reports, technical papers, and articles.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | URL Summary | Easy | Summarize the Python Wikipedia article |
| 2 | YouTube Summary | Easy | Summarize the 'Python in 100 Seconds' YouTube video |
| 3 | Comparison Summary | Easy | Compare and summarize two articles about Python |
| 4 | Executive Summary | Medium | Read business_report.txt and write an executive summary |
| 5 | Technical Abstract | Medium | Read technical_paper.txt and write a technical abstract |
| 6 | Comparative Summary | Medium | Read two AI in healthcare articles and compare them |
| 7 | Multi-Level Summary | Hard | Read quantum_computing.txt and provide three levels of summary |
| 8 | Q&A Generation | Hard | Read renewable_energy.txt and generate a Q&A study guide |
| 9 | Sentiment Analysis Summary | Hard | Read social_media_impact.txt and include sentiment analysis in summary |

---

### 5. Gmail (`gmail`)

Tests the agent's ability to search, read, send, and manage emails via Gmail.

**Required Skills**: `gog` (Gmail skill)

**Setup**: Sends 3 benchmark test emails to the configured inbox (project update, invoice, and newsletter) to ensure tasks have real data to work with.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | Email Search | Easy | Find the most recent email with subject '[BENCHMARK TEST] Project Alpha Updates' |
| 2 | Email Send | Easy | Send a test email to the benchmark address |
| 3 | Email Data Extraction | Easy | Find the most recent '[BENCHMARK TEST] Invoice' email and extract the amount |
| 4 | Count Unread | Medium | How many unread emails do I have? |
| 5 | Search by Sender | Medium | Find emails from support@example.com |
| 6 | Label Management | Medium | Create a label called 'Important Projects' |
| 7 | Email with Attachment | Hard | Find emails with PDF attachments from last week |
| 8 | Draft Email | Hard | Draft an email to team@example.com about Q1 results |
| 9 | Email Summary | Hard | Summarize the last 5 emails in my inbox |

**Setup Requirements**:
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` — bot's Gmail OAuth credentials
- `GMAIL_BENCHMARK_EMAIL` — email address for sending test emails and validation
- `GMAIL_BOT_EMAIL` — bot's Gmail address

---

### 6. GitHub (`github`)

Tests the agent's ability to interact with GitHub repositories, issues, pull requests, and releases.

**Required Skills**: `steipete/github`

**Setup**: Seeds the test repository with real data via the GitHub API:
- 5 JavaScript source files committed to main branch (`src/utils.js`, `src/api.js`, `src/index.js`, `README.md`, `package.json`)
- 1 feature branch (`feature/benchmark-pr-branch`) with an additional commit
- 1 open pull request: "[BENCHMARK] Add error handler feature"
- 1 release tagged `v1.0.0-benchmark`

All seeded data is removed during cleanup.

**Tasks**:

| # | Name | Difficulty | Prompt |
|---|------|-----------|--------|
| 1 | Issue Creation | Easy | Create a new issue titled '[BENCHMARK TEST] Test Issue' |
| 2 | List Issues | Easy | List all open issues and show their titles |
| 3 | Repository Info | Easy | Get the repo description, star count, and fork count |
| 4 | Recent Commits | Medium | Show the last 5 commits with messages and authors |
| 5 | Pull Request List | Medium | List all open pull requests |
| 6 | Issue Labels | Medium | What labels are available in the repository? |
| 7 | Contributor Stats | Hard | Who are the top 3 contributors by commit count? |
| 8 | File Contents | Hard | Get the contents of `src/utils.js` — what functions does it define? |
| 9 | Release Info | Hard | What was the latest release and when was it published? |

**Setup Requirements**:
- `GITHUB_TOKEN` — personal access token with `repo` scope for the benchmark account
- `GITHUB_TEST_REPO_OWNER` — owner of the test repository
- `GITHUB_TEST_REPO_NAME` — name of the test repository

---

### 7. Compound (`compound`)

Tests the agent's ability to chain multiple skills together in a single task. Each task requires 2–3 skills to be used in sequence, where the output of one feeds into the next.

**Required Skills**: `steipete/weather`, `tavily-search`, `steipete/github`, `steipete/summarize`

**Setup**: Uses the same GitHub test repository as the GitHub scenario. No additional local files needed. GitHub issues created during tasks are left open for inspection after the run.

**Tasks**:

| # | Name | Difficulty | Skills | Prompt |
|---|------|-----------|--------|--------|
| 1 | Weather + Web Research | Easy | weather + tavily | Check weather in Tokyo, then search for travel tips and packing recommendations |
| 2 | Web Search + Summarize | Easy | tavily + summarize | Search for a Python async article, then summarize the key points |
| 3 | GitHub + Summarize | Easy | github + summarize | Read `src/utils.js` from the repo, then summarize its purpose and functions |
| 4 | Weather + GitHub Issue | Medium | weather + github | Check weather in London, file a GitHub issue reporting the conditions |
| 5 | Web Research + GitHub Issue | Medium | tavily + github | Research async programming best practices, file a GitHub issue with findings |
| 6 | Multi-City Weather + Context | Medium | weather + tavily | Compare weather in London, Tokyo, and Paris with web context |
| 7 | GitHub Repo + Web Research | Hard | github + tavily | Get repo info then research the technology stack online |
| 8 | Web + Weather + GitHub Chain | Hard | tavily + weather + github | Search AI news, check weather, file a GitHub issue combining both |
| 9 | Research + Summarize + GitHub | Hard | tavily + summarize + github | Research ML in healthcare, summarize findings, file GitHub issue with summary |

**Setup Requirements**:
- `GITHUB_TOKEN` — personal access token with `repo` scope
- `GITHUB_TEST_REPO_OWNER` — owner of the test repository
- `GITHUB_TEST_REPO_NAME` — name of the test repository

---

## Understanding Results

### Console Output

At the start of each run, all scenarios and their tasks are printed with prompts:

```
============================================================
OpenClaw Benchmark Suite
Mode: async
Running 6 scenario(s): File Manipulation, Weather, ...
============================================================

Scenarios to run:

1. GitHub
   Description: Tests agent's ability to interact with GitHub repos, issues, and PRs
   Required skills: steipete/github
   Tasks (9):
      1. Issue Creation [EASY]
         Create a new issue in the repository owner/repo with the title '[BENCHMARK TEST]...
      2. List Issues [EASY]
         List all open issues in the repository owner/repo. Show me the issue titles.
      ...

============================================================
```

After each scenario completes:

```
------------------------------------------------------------
Scenario: GitHub
Duration: 458.23s
Tasks passed: 9/9
Average accuracy: 100.0%
Average latency: 51.03s
------------------------------------------------------------
```

### JSON Export

```bash
just bench all output=results.json
```

```json
{
  "scenarios": [
    {
      "scenario_name": "GitHub",
      "total_duration": 458.23,
      "all_tasks_passed": true,
      "average_accuracy": 100.0,
      "average_latency": 51.03,
      "task_results": [
        {
          "task_name": "Issue Creation",
          "success": true,
          "latency": 47.01,
          "accuracy_score": 100.0,
          "conversation_turns": 2,
          "completion_reason": "goal_achieved"
        }
      ]
    }
  ],
  "summary": {
    "total_scenarios": 6,
    "total_tasks": 54,
    "tasks_passed": 50,
    "overall_accuracy": 92.6
  }
}
```

### Scoring

Each task is scored **binary**: 100% (pass) or 0% (fail). Validation checks:
- Presence of required keywords in bot response
- Absence of "no data" / error phrases for tasks that require real data
- Specific content matches (e.g., file names, issue titles)

**Multi-turn conversations**: Each task allows up to 10 turns. The AI agent guides the conversation and signals completion when the goal is achieved.

---

## Architecture

```
benchmarks/
├── base.py                      # Core classes (ScenarioBase, BenchmarkTask, TaskResult)
├── ai_agent.py                  # Multi-turn conversation AI agent
├── skill_checker.py             # Skill availability detection
├── scenario_factory.py          # Scenario instantiation with config
├── remote_workspace.py          # SSH-based remote file validation
├── scenarios/
│   ├── file_scenario.py         # File manipulation (9 tasks)
│   ├── weather_scenario.py      # Weather queries (9 tasks)
│   ├── web_scenario.py          # Web search (9 tasks)
│   ├── summarize_scenario.py    # Content summarization (9 tasks)
│   ├── gmail_scenario.py        # Gmail operations (9 tasks)
│   ├── github_scenario.py       # GitHub operations (9 tasks)
│   └── compound_scenario.py     # Multi-skill compound tasks (9 tasks)
├── setup/
│   ├── file_setup.py            # Create test workspace files
│   ├── gmail_setup.py           # Send benchmark emails
│   └── github_setup.py          # Seed/cleanup GitHub repo data
└── validators/
    ├── file_validator.py        # Validate file task outputs
    ├── weather_validator.py     # Validate weather responses
    ├── web_validator.py         # Validate web search results
    ├── summarize_validator.py   # Validate summaries
    ├── gmail_validator.py       # Validate Gmail task outputs
    ├── github_validator.py      # Validate GitHub task outputs
    └── compound_validator.py    # Validate compound multi-skill outputs
```

---

## Troubleshooting

### Bot not responding / timeout
- Verify bot is running and the required skill is installed
- Check `OPENCLAW_BOT_USERNAME` in `.env`
- Increase `CONVERSATION_TIMEOUT` if tasks are slow

### Scenario skipped (missing skills)
- In local mode: install the required skill on your local OpenClaw instance
- In Telegram mode: skill detection is skipped — all scenarios run regardless

### GitHub seeding failures
- Ensure `GITHUB_TOKEN` has `repo` scope
- Ensure the test repo exists and is accessible with the token
- Check if a previous run's cleanup failed (stale branch/PR/release may block re-seeding)

### Gmail setup failures
- Refresh token may be expired — re-run `uv run python tools/get_gmail_token.py`
- Ensure `GMAIL_BENCHMARK_EMAIL` is set and can receive mail

### File scenario failures (remote mode)
- SSH credentials must be configured: `BOT_SSH_KEY_PATH` or `BOT_SSH_PASSWORD`
- The bot workspace path must match `BOT_WORKSPACE_PATH`

---

## Related Documentation

- [README.md](README.md) — Main project documentation
- [QUICKSTART.md](QUICKSTART.md) — Quick start guide
- [.env.example](.env.example) — All configuration options
