#!/usr/bin/env python3
"""Analyze a sweep log and print two summary tables:

1. Scenario x Model pass rates with avg tokens/task
2. Overall efficiency ranking

Usage:
    python analyze_sweep.py                          # uses latest sweep log
    python analyze_sweep.py logs/sweep_YYYYMMDD.log  # specific log file
"""

import re
import os
import sys
import glob


MODEL_SHORT_NAMES = {
    "openrouter/deepseek/deepseek-v3.2": "DS-v3.2",
    "anthropic/claude-sonnet-4-5": "Sonnet",
    "anthropic/claude-haiku-4-5": "Haiku",
    "openai/gpt-5.2": "GPT-5.2",
    "openai/gpt-5-mini": "GPT-5m",
    "openrouter/x-ai/grok-4.1-fast": "Grok",
    "openrouter/google/gemini-2.5-flash": "Gemini",
    "openrouter/openai/gpt-oss-120b": "OSS-120B",
    "openrouter/mistralai/mistral-nemo": "Mistral-Nemo",
    "openrouter/google/gemma-3-27b-it:free": "Gemma3-27B",
    "openrouter/qwen/qwen3-coder:free": "Qwen3-Coder",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free": "Llama3.3-70B",
    "openrouter/z-ai/glm-4.5-air:free": "GLM-4.5",
    "openrouter/qwen/qwen3-235b-a22b-thinking-2507": "Qwen3-235B",
    "anthropic/claude-opus-4-6": "Opus",
}

TASKS_PER_SCENARIO = 9
MIN_PASS_RATE_TO_SHOW = 0.01  # hide models with <1% pass rate


def short_name(model_id: str) -> str:
    return MODEL_SHORT_NAMES.get(model_id, model_id.split("/")[-1])


def find_latest_log(log_dir: str = "logs") -> str:
    logs = glob.glob(os.path.join(log_dir, "sweep_*.log"))
    if not logs:
        print(f"No sweep logs found in {log_dir}/", file=sys.stderr)
        sys.exit(1)
    return max(logs, key=os.path.getmtime)


def parse_log(filepath: str):
    with open(filepath) as f:
        lines = f.readlines()

    model = ""
    scenario = ""
    current_task = None
    models_seen = []
    results = {}          # (scenario, model) -> {task: bool}
    task_tokens = {}      # (scenario, model, task) -> int (total tokens)
    scenario_order = []

    for line in lines:
        m = re.search(r"Switching local openclaw model to: (.+)", line)
        if m:
            model = m.group(1).strip()
            if model not in models_seen:
                models_seen.append(model)
            continue

        m = re.search(r"SCENARIO START: (.+?) =", line)
        if m:
            scenario = m.group(1).strip()
            if scenario not in scenario_order:
                scenario_order.append(scenario)
            continue

        m = re.search(r"TASK (\d+)/(\d+): (.+?) =", line)
        if m:
            current_task = m.group(3).strip()
            key = (scenario, model)
            if key not in results:
                results[key] = {}
            if current_task not in results[key]:
                results[key][current_task] = False  # default: fail (timeout counts as fail)
            continue

        m = re.search(
            r"Multi-turn task completed:.*accuracy=([0-9.]+)"
            r".*tokens: in=(\d+) out=(\d+) reasoning=(\d+) cache_read=(\d+)",
            line,
        )
        if m and current_task and model:
            acc = float(m.group(1))
            key = (scenario, model)
            if key not in results:
                results[key] = {}
            results[key][current_task] = acc >= 100.0

            tok_total = int(m.group(1 + 1)) + int(m.group(2 + 1)) + int(m.group(3 + 1)) + int(m.group(4 + 1))
            task_tokens[(scenario, model, current_task)] = tok_total
            continue

    return models_seen, results, task_tokens, scenario_order


def fmt_tokens(n: float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    return f"{n / 1000:.0f}K"


def print_table(models, results, task_tokens, scenarios):
    # Compute totals to filter models
    totals_pass = {}
    totals_tasks = {}
    totals_tok = {}
    totals_completed = {}

    for mdl in models:
        totals_pass[mdl] = 0
        totals_tasks[mdl] = 0
        totals_tok[mdl] = 0
        totals_completed[mdl] = 0
        for scen in scenarios:
            key = (scen, mdl)
            if key in results:
                passed = sum(1 for v in results[key].values() if v)
                totals_pass[mdl] += passed
                totals_tasks[mdl] += TASKS_PER_SCENARIO
                for task in results[key]:
                    tkey = (scen, mdl, task)
                    if tkey in task_tokens:
                        totals_tok[mdl] += task_tokens[tkey]
                        totals_completed[mdl] += 1

    # Filter out models below threshold
    visible = [
        m for m in models
        if totals_tasks[m] > 0 and totals_pass[m] / totals_tasks[m] >= MIN_PASS_RATE_TO_SHOW
    ]

    cols = [short_name(m) for m in visible]

    # --- Table 1: Scenario x Model with tokens/task ---
    print("## Scenario x Model — pass rate (avg tokens/task)\n")
    print("| Scenario |", " | ".join(cols), "|")
    print("|----------|" + "|".join([" ---:" for _ in cols]) + "|")

    for scen in scenarios:
        row = []
        for mdl in visible:
            key = (scen, mdl)
            if key in results:
                passed = sum(1 for v in results[key].values() if v)
                scen_tok = 0
                scen_completed = 0
                for task in results[key]:
                    tkey = (scen, mdl, task)
                    if tkey in task_tokens:
                        scen_tok += task_tokens[tkey]
                        scen_completed += 1
                if scen_completed > 0:
                    avg = scen_tok / scen_completed
                    row.append(f"{passed}/{TASKS_PER_SCENARIO} ({fmt_tokens(avg)}/t)")
                else:
                    row.append(f"{passed}/{TASKS_PER_SCENARIO}")
            else:
                row.append("--")
        print(f"| **{scen}** | " + " | ".join(row) + " |")

    # Total row
    row = []
    for mdl in visible:
        p = totals_pass[mdl]
        t = totals_tasks[mdl]
        comp = totals_completed[mdl]
        tok = totals_tok[mdl]
        if t > 0 and comp > 0:
            avg = tok / comp
            row.append(f"**{p}/{t} ({fmt_tokens(avg)}/t)**")
        elif t > 0:
            row.append(f"**{p}/{t}**")
        else:
            row.append("--")
    print(f"| **TOTAL** | " + " | ".join(row) + " |")

    # Success rate row (percentage only)
    row = []
    for mdl in visible:
        p = totals_pass[mdl]
        t = totals_tasks[mdl]
        if t > 0:
            row.append(f"**{p * 100 / t:.0f}%**")
        else:
            row.append("--")
    print(f"| **Success Rate** | " + " | ".join(row) + " |")

    # --- Table 2: Efficiency ranking ---
    print("\n## Efficiency ranking\n")
    print("| Rank | Model | Pass Rate | Avg Tokens/Task |")
    print("|------|-------|-----------|-----------------|")

    ranked = sorted(
        visible,
        key=lambda m: (-totals_pass[m] / max(totals_tasks[m], 1), totals_tok[m] / max(totals_completed[m], 1)),
    )
    for i, mdl in enumerate(ranked, 1):
        p = totals_pass[mdl]
        t = totals_tasks[mdl]
        comp = totals_completed[mdl]
        tok = totals_tok[mdl]
        rate = f"{p * 100 / t:.0f}%" if t > 0 else "--"
        avg_tok = fmt_tokens(tok / comp) if comp > 0 else "--"
        print(f"| {i} | **{short_name(mdl)}** | {rate} ({p}/{t}) | {avg_tok} |")


def main():
    if len(sys.argv) > 1:
        logfile = sys.argv[1]
    else:
        logfile = find_latest_log()

    if not os.path.exists(logfile):
        print(f"File not found: {logfile}", file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(logfile)
    print(f"# Sweep Analysis: {os.path.basename(logfile)} ({size / 1024 / 1024:.1f}MB)\n")

    models, results, task_tokens, scenarios = parse_log(logfile)
    print_table(models, results, task_tokens, scenarios)


if __name__ == "__main__":
    main()
