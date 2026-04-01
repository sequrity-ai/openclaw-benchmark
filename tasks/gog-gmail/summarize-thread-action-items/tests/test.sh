#!/bin/bash
# Test: summarize-thread-action-items — must mention jake, priya, tom
set -e

python3 - <<'PYEOF'
import sys, os

reward_dir = os.environ.get("REWARD_DIR", "/tmp")
reward_file = os.path.join(reward_dir, "reward.txt")

def fail(reason=""):
    print(f"FAIL: {reason}", file=sys.stderr)
    with open(reward_file, "w") as f: f.write("0")
    sys.exit(0)

def pass_test(reason=""):
    print(f"PASS: {reason}")
    with open(reward_file, "w") as f: f.write("1")
    sys.exit(0)

try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read().lower()
except Exception as e:
    fail(f"Could not read response file: {e}")

missing = []
if "jake" not in response: missing.append("'jake'")
if "priya" not in response: missing.append("'priya'")
if "tom" not in response: missing.append("'tom'")

if not missing:
    pass_test("Response contains 'jake', 'priya', and 'tom'")
else:
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
