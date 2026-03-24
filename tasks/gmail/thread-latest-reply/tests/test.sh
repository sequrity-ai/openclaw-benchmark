#!/bin/bash
# Test: thread-latest-reply
# Verifies that the agent identifies Marcus Webb and mentions "option b".

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

has_marcus = "marcus" in response
has_option_b = "option b" in response

if has_marcus and has_option_b:
    pass_test("Response contains 'marcus' and 'option b'")
else:
    missing = []
    if not has_marcus:
        missing.append("'marcus'")
    if not has_option_b:
        missing.append("'option b'")
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
