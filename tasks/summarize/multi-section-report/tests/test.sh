#!/bin/bash
# Test: multi-section-report
# Check that response mentions NovaTech and key financial metrics.

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

if "novatech" not in response:
    fail("Response does not mention 'novatech'")

if "4.2" not in response and "18" not in response:
    fail("Response does not mention revenue '$4.2' million or '18%' growth")

pass_test("Response mentions 'novatech' and key financial metrics")
PYEOF
