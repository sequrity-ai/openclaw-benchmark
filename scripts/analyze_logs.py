#!/usr/bin/env python3
"""Analyze benchmark JSON result files and produce a leaderboard table.

Usage:
    python scripts/analyze_logs.py                          # all results_*.json in cwd
    python scripts/analyze_logs.py results_gpt5_mini.json   # specific file(s)
    python scripts/analyze_logs.py results_*.json           # glob
"""

import json
import os
import sys
import glob


def load_result(filepath: str) -> dict:
    """Load a benchmark result JSON and extract summary stats."""
    with open(filepath) as f:
        data = json.load(f)

    config = data.get("config", {})
    model = config.get("bot_model", os.path.basename(filepath))
    summary = data.get("summary", {})
    scenarios = data.get("scenarios", [])

    total_input = sum(sc.get("total_input_tokens", 0) for sc in scenarios)
    total_output = sum(sc.get("total_output_tokens", 0) for sc in scenarios)
    total_reasoning = sum(sc.get("total_reasoning_tokens", 0) for sc in scenarios)
    total_cache = sum(sc.get("total_cache_read_tokens", 0) for sc in scenarios)
    total_tokens = sum(sc.get("total_tokens", 0) for sc in scenarios)

    mode = config.get("mode", "multi_turn")

    return {
        "file": os.path.basename(filepath),
        "model": model,
        "mode": mode,
        "tasks_passed": summary.get("tasks_passed", 0),
        "total_tasks": summary.get("total_tasks", 0),
        "accuracy": summary.get("overall_accuracy", 0.0),
        "input_tokens": total_input,
        "output_tokens": total_output,
        "reasoning_tokens": total_reasoning,
        "cache_tokens": total_cache,
        "total_tokens": total_tokens,
        "scenarios": scenarios,
    }


def fmt_tokens(n: int) -> str:
    """Format token count with commas."""
    return f"{n:,}"


def print_leaderboard(results: list[dict]) -> None:
    """Print a markdown leaderboard table sorted by accuracy."""
    results.sort(key=lambda r: r["accuracy"], reverse=True)

    print("| Model | Mode | Tasks Passed | Accuracy | Input Tokens | Output Tokens | Cache Read | Total Tokens |")
    print("|---|---|---|---|---|---|---|---|")

    for r in results:
        mode_label = r.get("mode", "multi_turn")
        print(
            f"| {r['model']} "
            f"| {mode_label} "
            f"| {r['tasks_passed']}/{r['total_tasks']} "
            f"| {r['accuracy']:.1f}% "
            f"| {fmt_tokens(r['input_tokens'])} "
            f"| {fmt_tokens(r['output_tokens'])} "
            f"| {fmt_tokens(r['cache_tokens'])} "
            f"| {fmt_tokens(r['total_tokens'])} |"
        )

    print()


def print_scenario_breakdown(results: list[dict]) -> None:
    """Print per-scenario accuracy for each model."""
    # Collect all scenario names across all results
    all_scenarios: list[str] = []
    for r in results:
        for sc in r["scenarios"]:
            name = sc.get("scenario_name", "?")
            if name not in all_scenarios:
                all_scenarios.append(name)

    if not all_scenarios:
        return

    # Header
    header = "| Scenario |"
    sep = "|---|"
    for r in results:
        short = r["model"].split("/")[-1] if "/" in r["model"] else r["model"]
        header += f" {short} |"
        sep += "---|"
    print(header)
    print(sep)

    # Rows
    for sc_name in all_scenarios:
        row = f"| {sc_name} |"
        for r in results:
            match = [sc for sc in r["scenarios"] if sc.get("scenario_name") == sc_name]
            if match:
                sc = match[0]
                tasks = sc.get("task_results", [])
                passed = sum(1 for t in tasks if t.get("success", False))
                total = len(tasks)
                row += f" {passed}/{total} |"
            else:
                row += " - |"
        print(row)

    print()


def main():
    files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("results_*.json"))

    if not files:
        print("No result files found. Pass files as arguments or run from a directory with results_*.json.", file=sys.stderr)
        sys.exit(1)

    results = []
    for f in files:
        if not os.path.exists(f):
            print(f"Warning: {f} not found, skipping", file=sys.stderr)
            continue
        try:
            results.append(load_result(f))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: failed to parse {f}: {e}", file=sys.stderr)

    if not results:
        print("No valid results to display.", file=sys.stderr)
        sys.exit(1)

    print("# Benchmark Leaderboard\n")
    print_leaderboard(results)
    print("## Per-Scenario Breakdown\n")
    print_scenario_breakdown(results)


if __name__ == "__main__":
    main()
