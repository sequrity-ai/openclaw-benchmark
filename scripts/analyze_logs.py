#!/usr/bin/env python3
"""Analyze a benchmark log and its corresponding session JSONL to extract
per-task details: prompt, success, and Sequrity session ID.

Usage:
    python scripts/analyze_logs.py                                    # latest bench log
    python scripts/analyze_logs.py logs/bench_weather_20260224.log    # specific log
    python scripts/analyze_logs.py logs/bench_weather.log --session ~/path/to/session.jsonl
"""

import re
import os
import sys
import json
import glob
from datetime import datetime, timezone


SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")


# ---------------------------------------------------------------------------
# 1. Parse benchmark log
# ---------------------------------------------------------------------------

def parse_bench_log(filepath: str) -> list[dict]:
    """Return a list of task dicts extracted from the benchmark log."""
    with open(filepath) as f:
        lines = f.readlines()

    tasks: list[dict] = []
    current: dict | None = None

    for line in lines:
        # ===== TASK 1/9: Current Weather =====
        m = re.search(r"TASK (\d+)/(\d+): (.+?) =====", line)
        if m:
            current = {
                "index": int(m.group(1)),
                "total": int(m.group(2)),
                "name": m.group(3).strip(),
                "prompt": None,
                "description": None,
                "success": None,
                "accuracy": None,
                "turns": None,
                "latency": None,
                "tokens_in": None,
                "tokens_out": None,
                "task_start_ts": _extract_ts(line),
                "task_end_ts": None,
            }
            tasks.append(current)
            continue

        if current is None:
            continue

        # Task description: Bot reports SF all-time record high is 106°F set in 2017
        m = re.search(r"Task description: (.+)", line)
        if m:
            current["description"] = m.group(1).strip()
            continue

        # Agent message (turn 1): What is San Francisco's all-time record...
        m = re.search(r"Agent message \(turn 1\): (.+)", line)
        if m:
            prompt = m.group(1).strip()
            # Remove trailing "..." added by log truncation
            if prompt.endswith("..."):
                prompt = prompt[:-3]
            current["prompt"] = prompt
            continue

        # Multi-turn task completed: turns=2, success=True, accuracy=100.0, ...
        m = re.search(
            r"Multi-turn task completed: turns=(\d+), success=(True|False), "
            r"accuracy=([0-9.]+).*?latency=([0-9.]+)s.*?"
            r"tokens: in=(\d+) out=(\d+)",
            line,
        )
        if m:
            current["turns"] = int(m.group(1))
            current["success"] = m.group(2) == "True"
            current["accuracy"] = float(m.group(3))
            current["latency"] = float(m.group(4))
            current["tokens_in"] = int(m.group(5))
            current["tokens_out"] = int(m.group(6))
            current["task_end_ts"] = _extract_ts(line)
            continue

    return tasks


def _extract_ts(line: str) -> datetime | None:
    """Pull the leading timestamp from a log line."""
    m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+", line)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    return None


# ---------------------------------------------------------------------------
# 2. Parse session JSONL for Sequrity session IDs
# ---------------------------------------------------------------------------

def parse_session_ids(session_path: str) -> list[dict]:
    """Extract (timestamp, sequrity_session_id) from tool call IDs in the session JSONL.

    Sequrity encodes session IDs in tool call IDs as:
        tc-{session_uuid}-{call_uuid}
    where each UUID is 36 chars (8-4-4-4-12).
    Non-Sequrity tool calls use different formats (e.g. toolu_*).
    """
    entries: list[dict] = []

    with open(session_path) as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg = obj.get("message", {})
            ts_str = obj.get("timestamp", "")
            content = msg.get("content", [])

            if not isinstance(content, list):
                continue

            for item in content:
                if item.get("type") == "toolCall":
                    tc_id = item.get("id", "")
                    session_id = _extract_sequrity_session(tc_id)
                    if session_id:
                        ts = _parse_iso_ts(ts_str)
                        if ts:
                            entries.append({
                                "timestamp": ts,
                                "session_id": session_id,
                                "tool": item.get("name", ""),
                                "tc_id": tc_id,
                            })

    return entries


def _extract_sequrity_session(tc_id: str) -> str | None:
    """Extract the Sequrity session UUID from a tool call ID.

    Format: tc-{uuid1}-{uuid2}  where uuid = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars)
    """
    if not tc_id.startswith("tc-"):
        return None
    rest = tc_id[3:]  # strip "tc-"
    # First UUID is 36 chars
    if len(rest) < 37:
        return None
    candidate = rest[:36]
    # Validate UUID pattern
    if re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", candidate):
        return candidate
    return None


def _parse_iso_ts(ts_str: str) -> datetime | None:
    if not ts_str:
        return None
    try:
        # Handle "2026-02-24T08:52:44.157Z"
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 3. Match tasks to session IDs
# ---------------------------------------------------------------------------

def match_tasks_to_sessions(tasks: list[dict], session_entries: list[dict]) -> None:
    """For each task, find the Sequrity session ID(s) that were active during it."""
    for task in tasks:
        start = task.get("task_start_ts")
        end = task.get("task_end_ts")
        if not start or not end:
            task["session_ids"] = []
            continue

        # Find all tool calls that fall within this task's time window
        ids_in_window = set()
        for entry in session_entries:
            if start <= entry["timestamp"] <= end:
                ids_in_window.add(entry["session_id"])

        task["session_ids"] = sorted(ids_in_window)


# ---------------------------------------------------------------------------
# 4. Find session JSONL
# ---------------------------------------------------------------------------

def find_session_jsonl(bench_log: str) -> str | None:
    """Find the most likely session JSONL for a benchmark log by modification time."""
    if not os.path.isdir(SESSIONS_DIR):
        return None

    # Get benchmark log modification time
    bench_mtime = os.path.getmtime(bench_log)

    # Find session files modified close to the benchmark log
    candidates = glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl"))
    if not candidates:
        return None

    # Pick the session file whose mtime is closest to (but not before start of) the bench log
    best = None
    best_diff = float("inf")
    for c in candidates:
        mtime = os.path.getmtime(c)
        diff = abs(mtime - bench_mtime)
        if diff < best_diff:
            best_diff = diff
            best = c

    return best


def find_latest_bench_log(log_dir: str = "logs") -> str:
    logs = glob.glob(os.path.join(log_dir, "bench_*.log"))
    if not logs:
        print(f"No bench logs found in {log_dir}/", file=sys.stderr)
        sys.exit(1)
    return max(logs, key=os.path.getmtime)


# ---------------------------------------------------------------------------
# 5. Output
# ---------------------------------------------------------------------------

def print_report(tasks: list[dict], session_path: str | None, bench_log: str) -> None:
    print(f"# Benchmark Log Analysis: {os.path.basename(bench_log)}\n")
    if session_path:
        print(f"Session file: `{os.path.basename(session_path)}`\n")
    else:
        print("Session file: (not found — session IDs unavailable)\n")

    # Collect unique session IDs
    all_session_ids = set()
    for t in tasks:
        for sid in t.get("session_ids", []):
            all_session_ids.add(sid)

    if all_session_ids:
        print(f"Sequrity session IDs seen: {len(all_session_ids)}")
        for sid in sorted(all_session_ids):
            count = sum(1 for t in tasks if sid in t.get("session_ids", []))
            print(f"  - `{sid}` ({count} tasks)")
        print()

    # Per-task table
    print("| # | Task | Prompt | Pass | Acc | Turns | Latency | Session ID |")
    print("|---|------|--------|------|-----|-------|---------|------------|")

    for t in tasks:
        idx = t["index"]
        name = t["name"]
        prompt = t.get("prompt") or t.get("description") or "(unknown)"
        # Truncate prompt for table readability
        if len(prompt) > 80:
            prompt = prompt[:77] + "..."
        success = "PASS" if t.get("success") else "FAIL" if t.get("success") is not None else "?"
        acc = f'{t["accuracy"]:.0f}%' if t.get("accuracy") is not None else "?"
        turns = str(t["turns"]) if t.get("turns") else "?"
        latency = f'{t["latency"]:.0f}s' if t.get("latency") is not None else "?"

        sids = t.get("session_ids", [])
        if not sids:
            sid_str = "(none/fallback)"
        elif len(sids) == 1:
            sid_str = f"`{sids[0][:8]}...`"
        else:
            sid_str = ", ".join(f"`{s[:8]}...`" for s in sids)

        print(f"| {idx} | {name} | {prompt} | {success} | {acc} | {turns} | {latency} | {sid_str} |")

    # Summary
    total = len(tasks)
    passed = sum(1 for t in tasks if t.get("success"))
    failed = sum(1 for t in tasks if t.get("success") is False)
    avg_latency = (
        sum(t["latency"] for t in tasks if t.get("latency") is not None)
        / max(sum(1 for t in tasks if t.get("latency") is not None), 1)
    )
    total_tokens = sum(
        (t.get("tokens_in") or 0) + (t.get("tokens_out") or 0) for t in tasks
    )

    print(f"\n**Summary:** {passed}/{total} passed, {failed} failed, "
          f"avg latency {avg_latency:.0f}s, {total_tokens:,} total tokens")

    # Session ID analysis
    if all_session_ids:
        if len(all_session_ids) == 1:
            print(f"\n**Session ID note:** All tasks used the same Sequrity session "
                  f"(`{list(all_session_ids)[0][:12]}...`). "
                  f"The `/new` command resets OpenClaw context but does NOT rotate the Sequrity session ID.")
        else:
            print(f"\n**Session ID note:** {len(all_session_ids)} distinct Sequrity session IDs observed.")


def main():
    # Parse args
    bench_log = None
    session_path = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--session" and i + 1 < len(args):
            session_path = os.path.expanduser(args[i + 1])
            i += 2
        else:
            bench_log = args[i]
            i += 1

    if not bench_log:
        bench_log = find_latest_bench_log()

    if not os.path.exists(bench_log):
        print(f"File not found: {bench_log}", file=sys.stderr)
        sys.exit(1)

    # Parse benchmark log
    tasks = parse_bench_log(bench_log)
    if not tasks:
        print(f"No tasks found in {bench_log}", file=sys.stderr)
        sys.exit(1)

    # Find/parse session JSONL for session IDs
    if not session_path:
        session_path = find_session_jsonl(bench_log)

    if session_path and os.path.exists(session_path):
        session_entries = parse_session_ids(session_path)
        match_tasks_to_sessions(tasks, session_entries)
    else:
        session_entries = []

    print_report(tasks, session_path, bench_log)


if __name__ == "__main__":
    main()
