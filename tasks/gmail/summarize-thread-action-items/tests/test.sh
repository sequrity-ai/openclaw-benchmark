#!/bin/bash
# Test: summarize-thread-action-items
# Verifies that the agent identifies Jake, Priya, and Tom as action item owners.

set -e

python3 - <<'PYEOF'
import sys
import os

reward_dir = os.environ.get("REWARD_DIR", "/tmp")
reward_file = os.path.join(reward_dir, "reward.txt")

def fail(reason=""):
    print(f"FAIL: {reason}", file=sys.stderr)
    with open(reward_file, "w") as f:
        f.write("0")
    sys.exit(0)

def pass_test(reason=""):
    print(f"PASS: {reason}")
    with open(reward_file, "w") as f:
        f.write("1")
    sys.exit(0)

try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read().lower()
except Exception as e:
    fail(f"Could not read response file: {e}")

has_jake = "jake" in response
has_priya = "priya" in response
has_tom = "tom" in response

if has_jake and has_priya and has_tom:
    pass_test("Response contains 'jake', 'priya', and 'tom'")
else:
    missing = []
    if not has_jake:
        missing.append("'jake'")
    if not has_priya:
        missing.append("'priya'")
    if not has_tom:
        missing.append("'tom'")
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
