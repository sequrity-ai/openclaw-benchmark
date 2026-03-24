#!/bin/bash
# Test: extract-meeting-details
# Verifies that the agent reports details containing "april" and "zoom".

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

has_april = "april" in response
has_zoom = "zoom" in response

if has_april and has_zoom:
    pass_test("Response contains 'april' and 'zoom'")
else:
    missing = []
    if not has_april:
        missing.append("'april'")
    if not has_zoom:
        missing.append("'zoom'")
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
