#!/bin/bash
# Test: product-review-summary
# Check that response mentions BlueAir and the rating 4.

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

if "blueair" not in response:
    fail("Response does not mention 'blueair'")

if "4" not in response:
    fail("Response does not mention the rating '4'")

pass_test("Response mentions 'blueair' and the rating '4'")
PYEOF
