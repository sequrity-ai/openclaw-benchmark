"""Benchmark runner for Telegram bot performance testing."""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from config import TelegramConfig
from telegram_client import TelegramClient, TelegramSession

logger = logging.getLogger(__name__)


class BenchmarkType(Enum):
    """Types of benchmarks that can be run."""

    LATENCY = "latency"  # Simple query response time
    MULTI_TURN = "multi_turn"  # Multiple conversation turns
    CONCURRENT = "concurrent"  # Multiple simultaneous sessions
    ACCURACY = "accuracy"  # Task completion accuracy


@dataclass
class BenchmarkMetrics:
    """Metrics collected during a benchmark run."""

    benchmark_type: str
    start_time: float
    end_time: float
    total_duration: float
    messages_sent: int
    messages_received: int
    success_count: int
    error_count: int
    response_times: list[float] = field(default_factory=list)
    error_messages: list[str] = field(default_factory=list)
    additional_data: dict[str, Any] = field(default_factory=dict)

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0

    @property
    def min_response_time(self) -> float:
        """Get minimum response time."""
        return min(self.response_times) if self.response_times else 0.0

    @property
    def max_response_time(self) -> float:
        """Get maximum response time."""
        return max(self.response_times) if self.response_times else 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "benchmark_type": self.benchmark_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "response_times": {
                "avg": self.avg_response_time,
                "min": self.min_response_time,
                "max": self.max_response_time,
                "all": self.response_times,
            },
            "errors": self.error_messages,
            "additional_data": self.additional_data,
        }


@dataclass
class BenchmarkScenario:
    """Defines a benchmark scenario to run."""

    name: str
    benchmark_type: BenchmarkType
    messages: list[str]
    num_sessions: int = 1
    wait_for_response: bool = True
    response_timeout: float = 30.0
    inter_message_delay: float = 1.0


class BenchmarkRunner:
    """Runs benchmarks against Telegram bot."""

    def __init__(self, config: TelegramConfig):
        """Initialize benchmark runner.

        Args:
            config: Telegram configuration
        """
        self.config = config
        self.results: list[BenchmarkMetrics] = []

    async def run_scenario_async(
        self, scenario: BenchmarkScenario, chat_id: int
    ) -> BenchmarkMetrics:
        """Run a benchmark scenario asynchronously.

        Args:
            scenario: Benchmark scenario to run
            chat_id: Chat ID to use for testing

        Returns:
            Benchmark metrics
        """
        logger.info(f"Running scenario: {scenario.name} (async mode)")

        metrics = BenchmarkMetrics(
            benchmark_type=scenario.benchmark_type.value,
            start_time=time.time(),
            end_time=0.0,
            total_duration=0.0,
            messages_sent=0,
            messages_received=0,
            success_count=0,
            error_count=0,
        )

        async with TelegramClient(self.config) as client:
            if scenario.num_sessions == 1:
                # Single session scenario
                await self._run_single_session_async(client, scenario, chat_id, metrics)
            else:
                # Concurrent sessions scenario
                await self._run_concurrent_sessions_async(client, scenario, chat_id, metrics)

        metrics.end_time = time.time()
        metrics.total_duration = metrics.end_time - metrics.start_time
        self.results.append(metrics)

        logger.info(f"Scenario completed: {scenario.name}")
        logger.info(f"Success rate: {metrics.success_rate:.2f}%")
        logger.info(f"Avg response time: {metrics.avg_response_time:.2f}s")

        return metrics

    def run_scenario_sync(self, scenario: BenchmarkScenario, chat_id: int) -> BenchmarkMetrics:
        """Run a benchmark scenario synchronously.

        Args:
            scenario: Benchmark scenario to run
            chat_id: Chat ID to use for testing

        Returns:
            Benchmark metrics
        """
        logger.info(f"Running scenario: {scenario.name} (sync mode)")

        metrics = BenchmarkMetrics(
            benchmark_type=scenario.benchmark_type.value,
            start_time=time.time(),
            end_time=0.0,
            total_duration=0.0,
            messages_sent=0,
            messages_received=0,
            success_count=0,
            error_count=0,
        )

        with TelegramClient(self.config) as client:
            self._run_single_session_sync(client, scenario, chat_id, metrics)

        metrics.end_time = time.time()
        metrics.total_duration = metrics.end_time - metrics.start_time
        self.results.append(metrics)

        logger.info(f"Scenario completed: {scenario.name}")
        logger.info(f"Success rate: {metrics.success_rate:.2f}%")
        logger.info(f"Avg response time: {metrics.avg_response_time:.2f}s")

        return metrics

    async def _run_single_session_async(
        self,
        client: TelegramClient,
        scenario: BenchmarkScenario,
        chat_id: int,
        metrics: BenchmarkMetrics,
    ) -> None:
        """Run a single session benchmark asynchronously."""
        session = TelegramSession(client, chat_id)

        for i, message in enumerate(scenario.messages):
            try:
                start_time = time.time()
                response = await session.send_message_async(
                    message,
                    wait_for_response=scenario.wait_for_response,
                    timeout=scenario.response_timeout,
                )
                response_time = time.time() - start_time

                metrics.messages_sent += 1

                if response:
                    metrics.messages_received += 1
                    metrics.success_count += 1
                    metrics.response_times.append(response_time)
                    logger.debug(f"Message {i+1}/{len(scenario.messages)}: {response_time:.2f}s")
                else:
                    metrics.error_count += 1
                    metrics.error_messages.append(f"No response for message: {message[:50]}")

                # Inter-message delay
                if i < len(scenario.messages) - 1:
                    await asyncio.sleep(scenario.inter_message_delay)

            except Exception as e:
                logger.error(f"Error sending message: {e}")
                metrics.error_count += 1
                metrics.error_messages.append(str(e))

        metrics.additional_data["session_duration"] = session.get_duration()

    def _run_single_session_sync(
        self,
        client: TelegramClient,
        scenario: BenchmarkScenario,
        chat_id: int,
        metrics: BenchmarkMetrics,
    ) -> None:
        """Run a single session benchmark synchronously."""
        session = TelegramSession(client, chat_id)

        for i, message in enumerate(scenario.messages):
            try:
                start_time = time.time()
                response = session.send_message_sync(
                    message,
                    wait_for_response=scenario.wait_for_response,
                    timeout=scenario.response_timeout,
                )
                response_time = time.time() - start_time

                metrics.messages_sent += 1

                if response:
                    metrics.messages_received += 1
                    metrics.success_count += 1
                    metrics.response_times.append(response_time)
                    logger.debug(f"Message {i+1}/{len(scenario.messages)}: {response_time:.2f}s")
                else:
                    metrics.error_count += 1
                    metrics.error_messages.append(f"No response for message: {message[:50]}")

                # Inter-message delay
                if i < len(scenario.messages) - 1:
                    time.sleep(scenario.inter_message_delay)

            except Exception as e:
                logger.error(f"Error sending message: {e}")
                metrics.error_count += 1
                metrics.error_messages.append(str(e))

        metrics.additional_data["session_duration"] = session.get_duration()

    async def _run_concurrent_sessions_async(
        self,
        client: TelegramClient,
        scenario: BenchmarkScenario,
        chat_id: int,
        metrics: BenchmarkMetrics,
    ) -> None:
        """Run concurrent sessions benchmark asynchronously."""
        logger.info(f"Running {scenario.num_sessions} concurrent sessions")

        async def run_session_task(session_id: int) -> dict[str, Any]:
            """Run a single session task."""
            session_metrics = {
                "session_id": session_id,
                "messages_sent": 0,
                "messages_received": 0,
                "response_times": [],
                "errors": [],
            }

            session = TelegramSession(client, chat_id)

            for message in scenario.messages:
                try:
                    start_time = time.time()
                    response = await session.send_message_async(
                        f"[Session {session_id}] {message}",
                        wait_for_response=scenario.wait_for_response,
                        timeout=scenario.response_timeout,
                    )
                    response_time = time.time() - start_time

                    session_metrics["messages_sent"] += 1

                    if response:
                        session_metrics["messages_received"] += 1
                        session_metrics["response_times"].append(response_time)
                    else:
                        session_metrics["errors"].append("No response")

                    await asyncio.sleep(scenario.inter_message_delay)

                except Exception as e:
                    session_metrics["errors"].append(str(e))

            return session_metrics

        # Run all sessions concurrently
        tasks = [run_session_task(i) for i in range(scenario.num_sessions)]
        session_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate metrics
        for result in session_results:
            if isinstance(result, Exception):
                metrics.error_count += 1
                metrics.error_messages.append(str(result))
            else:
                metrics.messages_sent += result["messages_sent"]
                metrics.messages_received += result["messages_received"]
                metrics.response_times.extend(result["response_times"])
                metrics.success_count += result["messages_received"]
                metrics.error_count += len(result["errors"])
                metrics.error_messages.extend(result["errors"])

        metrics.additional_data["num_sessions"] = scenario.num_sessions
        metrics.additional_data["concurrent"] = True

    def export_results(self, output_path: Path, format: str = "json") -> None:
        """Export benchmark results to file.

        Args:
            output_path: Path to output file
            format: Output format (json, csv, markdown)
        """
        if format == "json":
            self._export_json(output_path)
        elif format == "markdown":
            self._export_markdown(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Results exported to {output_path}")

    def _export_json(self, output_path: Path) -> None:
        """Export results as JSON."""
        data = {
            "timestamp": time.time(),
            "config": {
                "async_mode": self.config.async_mode,
                "openclaw_bot_username": self.config.openclaw_bot_username,
            },
            "results": [metrics.to_dict() for metrics in self.results],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def _export_markdown(self, output_path: Path) -> None:
        """Export results as Markdown."""
        lines = ["# Telegram Bot Benchmark Results", ""]
        lines.append(f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Async Mode:** {self.config.async_mode}")
        lines.append(f"**Bot Username:** {self.config.openclaw_bot_username}")
        lines.append("")

        for i, metrics in enumerate(self.results, 1):
            lines.append(f"## Benchmark {i}: {metrics.benchmark_type}")
            lines.append("")
            lines.append(f"- **Duration:** {metrics.total_duration:.2f}s")
            lines.append(f"- **Messages Sent:** {metrics.messages_sent}")
            lines.append(f"- **Messages Received:** {metrics.messages_received}")
            lines.append(f"- **Success Rate:** {metrics.success_rate:.2f}%")
            lines.append("")
            lines.append("### Response Times")
            lines.append(f"- **Average:** {metrics.avg_response_time:.2f}s")
            lines.append(f"- **Min:** {metrics.min_response_time:.2f}s")
            lines.append(f"- **Max:** {metrics.max_response_time:.2f}s")
            lines.append("")

            if metrics.error_messages:
                lines.append("### Errors")
                for error in metrics.error_messages[:10]:  # Limit to first 10 errors
                    lines.append(f"- {error}")
                lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))


# Pre-defined benchmark scenarios
EXAMPLE_SCENARIOS = [
    BenchmarkScenario(
        name="Simple Latency Test",
        benchmark_type=BenchmarkType.LATENCY,
        messages=["Hello!", "What's the weather today?", "Tell me a joke"],
        num_sessions=1,
        wait_for_response=True,
        response_timeout=30.0,
        inter_message_delay=2.0,
    ),
    BenchmarkScenario(
        name="Multi-turn Conversation",
        benchmark_type=BenchmarkType.MULTI_TURN,
        messages=[
            "I need help with a Python project",
            "Can you help me write a function to parse JSON?",
            "What libraries should I use?",
            "Show me an example",
            "Thanks!",
        ],
        num_sessions=1,
        wait_for_response=True,
        response_timeout=60.0,
        inter_message_delay=3.0,
    ),
]
