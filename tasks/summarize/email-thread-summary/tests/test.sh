#!/bin/bash
# Test: email-thread-summary
# Check that response mentions DevSummit and June or Hilton.

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

if "devsummit" not in response:
    fail("Response does not mention 'devsummit'")

if "june" not in response and "hilton" not in response:
    fail("Response does not mention 'june' or 'hilton'")

pass_test("Response mentions 'devsummit' and at least one of 'june' or 'hilton'")
PYEOF
