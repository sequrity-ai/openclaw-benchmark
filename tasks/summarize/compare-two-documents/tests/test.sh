#!/bin/bash
# Test: compare-two-documents
# Check that response mentions both teams and identifies the cheaper proposal.

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

if "alpha" not in response:
    fail("Response does not mention 'alpha'")

if "beta" not in response:
    fail("Response does not mention 'beta'")

if "35" not in response and "cheaper" not in response:
    fail("Response does not identify the cheaper proposal (no '35' or 'cheaper')")

pass_test("Response mentions both teams and identifies the cheaper proposal")
PYEOF
