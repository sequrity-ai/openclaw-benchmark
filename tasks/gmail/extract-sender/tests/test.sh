#!/bin/bash
# Test: extract-sender
# Verifies that the agent reports the sender's name containing "sarah" and "chen".

set -e

python3 - <<'PYEOF'
import sys
import os
import re

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

has_sarah = "sarah" in response
has_chen = "chen" in response

if has_sarah and has_chen:
    pass_test("Response contains 'sarah' and 'chen'")
else:
    missing = []
    if not has_sarah:
        missing.append("'sarah'")
    if not has_chen:
        missing.append("'chen'")
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
