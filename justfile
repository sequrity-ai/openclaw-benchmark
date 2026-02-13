# OpenClaw Telegram Benchmark Client - Justfile
# Run `just` or `just --list` to see available commands

# Default recipe - show help
default:
    @just --list

# Install dependencies with uv
install:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --group dev

# Run tests
test:
    uv run pytest -v

# Run tests with coverage
test-cov:
    uv run pytest --cov=. --cov-report=html --cov-report=term
    @echo "\nCoverage report generated in htmlcov/index.html"

# Run linter
lint:
    uv run ruff check .

# Format code
format:
    uv run ruff format .

# Check formatting without making changes
format-check:
    uv run ruff format --check .

# Test local OpenClaw connection
test-local:
    uv run openclaw-tg --local test

# Test Telegram bot connection
test-telegram:
    uv run openclaw-tg test

# List available benchmark scenarios with skill status
list-scenarios:
    uv run openclaw-tg --local list-scenarios

# Run file manipulation benchmark (local mode)
bench-file:
    uv run openclaw-tg --local benchmark-suite --scenario file

# Run web research benchmark (local mode)
bench-web:
    uv run openclaw-tg --local benchmark-suite --scenario web

# Run weather benchmark (local mode)
bench-weather:
    uv run openclaw-tg --local benchmark-suite --scenario weather

# Run all benchmarks (local mode, skip missing skills)
bench-all:
    uv run openclaw-tg --local benchmark-suite --scenario all

# Run all benchmarks with output file
bench-all-save output="benchmark_results.json":
    uv run openclaw-tg --local benchmark-suite --scenario all --output {{output}}

# Run benchmark in sync mode for debugging
bench-debug scenario="file":
    uv run openclaw-tg --local --sync benchmark-suite --scenario {{scenario}} -v

# Run benchmarks in Telegram mode (requires chat_id)
bench-telegram chat_id scenario="file":
    uv run openclaw-tg benchmark-suite {{chat_id}} --scenario {{scenario}}

# Clean up test artifacts
clean:
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf __pycache__
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    rm -f benchmark_*.json benchmark_*.md *_results.json *_results.md

# Clean up benchmark workspace
clean-workspace:
    rm -rf /tmp/openclaw_benchmark

# Full clean (includes dependencies)
clean-all: clean clean-workspace
    rm -rf .venv
    rm -rf uv.lock

# Run a quick health check
health:
    @echo "=== System Health Check ==="
    @echo "\n1. Python version:"
    @python3 --version
    @echo "\n2. UV installed:"
    @uv --version || echo "UV not installed"
    @echo "\n3. OpenClaw CLI:"
    @openclaw health || echo "OpenClaw not available"
    @echo "\n4. Virtual environment:"
    @test -d .venv && echo "✓ .venv exists" || echo "✗ .venv missing (run 'just install')"
    @echo "\n5. Dependencies:"
    @test -f uv.lock && echo "✓ uv.lock exists" || echo "✗ uv.lock missing"

# Show OpenClaw installed skills
skills:
    @openclaw skills list || echo "OpenClaw not available or no skills installed"

# Install a specific OpenClaw skill via clawhub
install-skill skill:
    clawhub install {{skill}}

# Create .env from example
setup-env:
    @test -f .env && echo ".env already exists" || cp .env.example .env
    @echo "✓ .env file ready. Edit it to add your TELEGRAM_BOT_TOKEN"

# Full setup: install deps, create .env, run tests
setup: setup-env install test
    @echo "\n✓ Setup complete! Ready to run benchmarks."
    @echo "Try: just test-local"

# Development mode: format, lint, test
dev: format lint test
    @echo "\n✓ All checks passed!"

# CI mode: check formatting, lint, test with coverage
ci: format-check lint test-cov
    @echo "\n✓ CI checks complete!"

# Watch mode for development (requires entr)
watch:
    find . -name "*.py" | entr -c just dev

# Run a custom benchmark scenario (provide scenario name, mode, and optional output)
# Usage: just bench file local results.json
#        just bench web telegram <chat_id> results.json
bench scenario="file" mode="local" chat_id="0" output="":
    #!/usr/bin/env bash
    if [ "{{mode}}" = "local" ]; then
        if [ -z "{{output}}" ]; then
            uv run openclaw-tg --local benchmark-suite --scenario {{scenario}}
        else
            uv run openclaw-tg --local benchmark-suite --scenario {{scenario}} --output {{output}}
        fi
    elif [ "{{mode}}" = "telegram" ]; then
        if [ "{{chat_id}}" = "0" ]; then
            echo "Error: chat_id required for Telegram mode"
            echo "Usage: just bench <scenario> telegram <chat_id> [output]"
            exit 1
        fi
        if [ -z "{{output}}" ]; then
            uv run openclaw-tg benchmark-suite {{chat_id}} --scenario {{scenario}}
        else
            uv run openclaw-tg benchmark-suite {{chat_id}} --scenario {{scenario}} --output {{output}}
        fi
    else
        echo "Error: mode must be 'local' or 'telegram'"
        exit 1
    fi

# Compare two benchmark results (requires jq)
compare result1 result2:
    #!/usr/bin/env bash
    echo "=== Benchmark Comparison ==="
    echo "\nResult 1: {{result1}}"
    jq -r '.summary | "Scenarios: \(.total_scenarios), Tasks: \(.total_tasks), Passed: \(.tasks_passed), Accuracy: \(.overall_accuracy)%"' {{result1}}
    echo "\nResult 2: {{result2}}"
    jq -r '.summary | "Scenarios: \(.total_scenarios), Tasks: \(.total_tasks), Passed: \(.tasks_passed), Accuracy: \(.overall_accuracy)%"' {{result2}}

# Generate benchmark report from JSON results
report results="benchmark_results.json":
    #!/usr/bin/env bash
    if [ ! -f "{{results}}" ]; then
        echo "Error: {{results}} not found"
        exit 1
    fi
    echo "=== Benchmark Report ==="
    jq -r '
        "Total Scenarios: \(.summary.total_scenarios)",
        "Total Tasks: \(.summary.total_tasks)",
        "Tasks Passed: \(.summary.tasks_passed)",
        "Overall Accuracy: \(.summary.overall_accuracy | round)%",
        "",
        "Scenarios:",
        (.scenarios[] | "  - \(.scenario_name): \(.task_results | map(select(.success)) | length)/\(.task_results | length) tasks passed, \(.average_accuracy | round)% accuracy")
    ' {{results}}

# Run minimal smoke test
smoke:
    @echo "Running smoke test (file scenario only)..."
    uv run openclaw-tg --local benchmark-suite --scenario file --no-setup

# Show project info
info:
    @echo "=== OpenClaw Telegram Benchmark Client ==="
    @echo "Version: 0.1.0"
    @echo "Python: $(python3 --version)"
    @echo "Location: $(pwd)"
    @echo ""
    @echo "Quick commands:"
    @echo "  just test-local      - Test local OpenClaw connection"
    @echo "  just list-scenarios  - Show available benchmarks"
    @echo "  just bench-all       - Run all benchmarks"
    @echo "  just health          - System health check"
    @echo ""
    @echo "Run 'just' to see all commands"
