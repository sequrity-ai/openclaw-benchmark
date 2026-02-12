"""Command-line interface for Telegram bot benchmarking."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from benchmark_runner import EXAMPLE_SCENARIOS, BenchmarkRunner, BenchmarkScenario
from benchmarks.scenarios import FileScenario, WebScenario
from config import TelegramConfig, load_config
from telegram_client import TelegramClient

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


async def test_connection_async(config: TelegramConfig) -> bool:
    """Test Telegram bot connection asynchronously.

    Args:
        config: Telegram configuration

    Returns:
        True if connection successful
    """
    try:
        async with TelegramClient(config) as client:
            bot_info = await client.get_me_async()
            logger.info(f"Connected to bot: {bot_info.get('username')} (ID: {bot_info.get('id')})")
            return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False


def test_connection_sync(config: TelegramConfig) -> bool:
    """Test Telegram bot connection synchronously.

    Args:
        config: Telegram configuration

    Returns:
        True if connection successful
    """
    try:
        with TelegramClient(config) as client:
            bot_info = client.get_me_sync()
            logger.info(f"Connected to bot: {bot_info.get('username')} (ID: {bot_info.get('id')})")
            return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False


async def send_message_async(config: TelegramConfig, chat_id: int, text: str) -> None:
    """Send a message asynchronously.

    Args:
        config: Telegram configuration
        chat_id: Chat ID to send to
        text: Message text
    """
    async with TelegramClient(config) as client:
        message = await client.send_message_async(chat_id, text)
        logger.info(f"Message sent (ID: {message.message_id})")


def send_message_sync(config: TelegramConfig, chat_id: int, text: str) -> None:
    """Send a message synchronously.

    Args:
        config: Telegram configuration
        chat_id: Chat ID to send to
        text: Message text
    """
    with TelegramClient(config) as client:
        message = client.send_message_sync(chat_id, text)
        logger.info(f"Message sent (ID: {message.message_id})")


async def run_benchmark_async(
    config: TelegramConfig, scenario: BenchmarkScenario, chat_id: int, output_path: Path | None
) -> None:
    """Run a benchmark scenario asynchronously.

    Args:
        config: Telegram configuration
        scenario: Benchmark scenario to run
        chat_id: Chat ID for testing
        output_path: Optional output path for results
    """
    runner = BenchmarkRunner(config)
    metrics = await runner.run_scenario_async(scenario, chat_id)

    # Print summary
    print("\n=== Benchmark Results ===")
    print(f"Benchmark Type: {metrics.benchmark_type}")
    print(f"Duration: {metrics.total_duration:.2f}s")
    print(f"Messages Sent: {metrics.messages_sent}")
    print(f"Messages Received: {metrics.messages_received}")
    print(f"Success Rate: {metrics.success_rate:.2f}%")
    print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
    print(f"Min Response Time: {metrics.min_response_time:.2f}s")
    print(f"Max Response Time: {metrics.max_response_time:.2f}s")

    if metrics.error_messages:
        print(f"\nErrors: {len(metrics.error_messages)}")
        for error in metrics.error_messages[:5]:
            print(f"  - {error}")

    if output_path:
        runner.export_results(output_path, format="markdown")
        print(f"\nResults exported to: {output_path}")


def run_benchmark_sync(
    config: TelegramConfig, scenario: BenchmarkScenario, chat_id: int, output_path: Path | None
) -> None:
    """Run a benchmark scenario synchronously.

    Args:
        config: Telegram configuration
        scenario: Benchmark scenario to run
        chat_id: Chat ID for testing
        output_path: Optional output path for results
    """
    runner = BenchmarkRunner(config)
    metrics = runner.run_scenario_sync(scenario, chat_id)

    # Print summary
    print("\n=== Benchmark Results ===")
    print(f"Benchmark Type: {metrics.benchmark_type}")
    print(f"Duration: {metrics.total_duration:.2f}s")
    print(f"Messages Sent: {metrics.messages_sent}")
    print(f"Messages Received: {metrics.messages_received}")
    print(f"Success Rate: {metrics.success_rate:.2f}%")
    print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
    print(f"Min Response Time: {metrics.min_response_time:.2f}s")
    print(f"Max Response Time: {metrics.max_response_time:.2f}s")

    if metrics.error_messages:
        print(f"\nErrors: {len(metrics.error_messages)}")
        for error in metrics.error_messages[:5]:
            print(f"  - {error}")

    if output_path:
        runner.export_results(output_path, format="markdown")
        print(f"\nResults exported to: {output_path}")


async def run_benchmark_suite_async(config: TelegramConfig, args) -> None:
    """Run benchmark suite asynchronously.

    Args:
        config: Telegram configuration
        args: Command-line arguments
    """
    async with TelegramClient(config) as client:
        # Determine which scenarios to run
        scenarios = []
        if args.scenario == "file" or args.scenario == "all":
            scenarios.append(FileScenario())
        if args.scenario == "web" or args.scenario == "all":
            scenarios.append(WebScenario())

        print(f"\n{'='*60}")
        print(f"OpenClaw Benchmark Suite")
        print(f"Running {len(scenarios)} scenario(s): {', '.join(s.name for s in scenarios)}")
        print(f"Mode: {'Async' if config.async_mode else 'Sync'}")
        print(f"Skip setup: {args.no_setup}")
        print(f"{'='*60}\n")

        all_results = []

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{len(scenarios)}] Running scenario: {scenario.name}")
            print(f"Description: {scenario.description}")
            print(f"Required skills: {', '.join(scenario.required_skills)}\n")

            result = await scenario.run_async(client, args.chat_id, skip_setup=args.no_setup)
            all_results.append(result)

            # Print summary
            print(f"\n{'-'*60}")
            print(f"Scenario: {result.scenario_name}")
            print(f"Duration: {result.total_duration:.2f}s")
            print(f"Tasks passed: {sum(1 for t in result.task_results if t.success)}/{len(result.task_results)}")
            print(f"Average accuracy: {result.average_accuracy:.1f}%")
            print(f"Average latency: {result.average_latency:.2f}s")
            print(f"{'-'*60}\n")

        # Export results if requested
        if args.output:
            export_data = {
                "config": {
                    "async_mode": config.async_mode,
                    "openclaw_bot_username": config.openclaw_bot_username,
                },
                "scenarios": [result.to_dict() for result in all_results],
                "summary": {
                    "total_scenarios": len(all_results),
                    "total_tasks": sum(len(r.task_results) for r in all_results),
                    "tasks_passed": sum(sum(1 for t in r.task_results if t.success) for r in all_results),
                    "overall_accuracy": sum(r.average_accuracy for r in all_results) / len(all_results) if all_results else 0.0,
                }
            }

            with open(args.output, "w") as f:
                json.dump(export_data, f, indent=2)

            print(f"\nResults exported to: {args.output}")


def run_benchmark_suite_sync(config: TelegramConfig, args) -> None:
    """Run benchmark suite synchronously.

    Args:
        config: Telegram configuration
        args: Command-line arguments
    """
    with TelegramClient(config) as client:
        scenarios = []
        if args.scenario == "file" or args.scenario == "all":
            scenarios.append(FileScenario())
        if args.scenario == "web" or args.scenario == "all":
            scenarios.append(WebScenario())

        print(f"\n{'='*60}")
        print(f"OpenClaw Benchmark Suite")
        print(f"Running {len(scenarios)} scenario(s): {', '.join(s.name for s in scenarios)}")
        print(f"Mode: {'Async' if config.async_mode else 'Sync'}")
        print(f"Skip setup: {args.no_setup}")
        print(f"{'='*60}\n")

        all_results = []

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n[{i}/{len(scenarios)}] Running scenario: {scenario.name}")
            print(f"Description: {scenario.description}")
            print(f"Required skills: {', '.join(scenario.required_skills)}\n")

            result = scenario.run_sync(client, args.chat_id, skip_setup=args.no_setup)
            all_results.append(result)

            print(f"\n{'-'*60}")
            print(f"Scenario: {result.scenario_name}")
            print(f"Duration: {result.total_duration:.2f}s")
            print(f"Tasks passed: {sum(1 for t in result.task_results if t.success)}/{len(result.task_results)}")
            print(f"Average accuracy: {result.average_accuracy:.1f}%")
            print(f"Average latency: {result.average_latency:.2f}s")
            print(f"{'-'*60}\n")

        if args.output:
            export_data = {
                "config": {
                    "async_mode": config.async_mode,
                    "openclaw_bot_username": config.openclaw_bot_username,
                },
                "scenarios": [result.to_dict() for result in all_results],
                "summary": {
                    "total_scenarios": len(all_results),
                    "total_tasks": sum(len(r.task_results) for r in all_results),
                    "tasks_passed": sum(sum(1 for t in r.task_results if t.success) for r in all_results),
                    "overall_accuracy": sum(r.average_accuracy for r in all_results) / len(all_results) if all_results else 0.0,
                }
            }

            with open(args.output, "w") as f:
                json.dump(export_data, f, indent=2)

            print(f"\nResults exported to: {args.output}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Telegram Bot Benchmarking CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--async",
        dest="async_mode",
        action="store_true",
        help="Use async mode (performance)",
    )
    parser.add_argument(
        "--sync",
        dest="async_mode",
        action="store_false",
        help="Use sync mode (debugging)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Test connection
    test_parser = subparsers.add_parser("test", help="Test Telegram bot connection")

    # Send message
    send_parser = subparsers.add_parser("send", help="Send a message to a chat")
    send_parser.add_argument("chat_id", type=int, help="Chat ID to send message to")
    send_parser.add_argument("text", help="Message text")

    # Run benchmark
    benchmark_parser = subparsers.add_parser("benchmark", help="Run a benchmark scenario")
    benchmark_parser.add_argument("chat_id", type=int, help="Chat ID for testing")
    benchmark_parser.add_argument(
        "--scenario",
        type=int,
        default=0,
        help=f"Scenario index (0-{len(EXAMPLE_SCENARIOS)-1})",
    )
    benchmark_parser.add_argument(
        "--output", "-o", type=Path, help="Output path for results (markdown)"
    )

    # List scenarios
    list_parser = subparsers.add_parser("list-scenarios", help="List available scenarios")

    # Benchmark suite
    suite_parser = subparsers.add_parser("benchmark-suite", help="Run benchmark suite")
    suite_parser.add_argument("chat_id", type=int, help="Chat ID for testing")
    suite_parser.add_argument(
        "--scenario",
        type=str,
        choices=["file", "web", "all"],
        default="all",
        help="Scenario to run (file, web, or all)",
    )
    suite_parser.add_argument("--no-setup", action="store_true", help="Skip setup phase")
    suite_parser.add_argument(
        "--output", "-o", type=Path, help="Output path for results (JSON)"
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Make sure you have a .env file with TELEGRAM_BOT_TOKEN set")
        return 1

    # Override async mode if specified
    if hasattr(args, "async_mode") and args.async_mode is not None:
        config.async_mode = args.async_mode

    logger.info(f"Running in {'async' if config.async_mode else 'sync'} mode")

    # Handle commands
    if args.command == "test":
        if config.async_mode:
            success = asyncio.run(test_connection_async(config))
        else:
            success = test_connection_sync(config)
        return 0 if success else 1

    elif args.command == "send":
        try:
            if config.async_mode:
                asyncio.run(send_message_async(config, args.chat_id, args.text))
            else:
                send_message_sync(config, args.chat_id, args.text)
            return 0
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return 1

    elif args.command == "benchmark":
        if args.scenario < 0 or args.scenario >= len(EXAMPLE_SCENARIOS):
            logger.error(f"Invalid scenario index: {args.scenario}")
            return 1

        scenario = EXAMPLE_SCENARIOS[args.scenario]
        logger.info(f"Running scenario: {scenario.name}")

        try:
            if config.async_mode:
                asyncio.run(run_benchmark_async(config, scenario, args.chat_id, args.output))
            else:
                run_benchmark_sync(config, scenario, args.chat_id, args.output)
            return 0
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return 1

    elif args.command == "list-scenarios":
        print("\nAvailable Benchmark Scenarios:")
        for i, scenario in enumerate(EXAMPLE_SCENARIOS):
            print(f"\n{i}. {scenario.name}")
            print(f"   Type: {scenario.benchmark_type.value}")
            print(f"   Messages: {len(scenario.messages)}")
            print(f"   Sessions: {scenario.num_sessions}")
        return 0

    elif args.command == "benchmark-suite":
        try:
            if config.async_mode:
                asyncio.run(run_benchmark_suite_async(config, args))
            else:
                run_benchmark_suite_sync(config, args)
            return 0
        except Exception as e:
            logger.error(f"Benchmark suite failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
