#!/bin/bash
# Test: find-subject
# Verifies that the agent reports the subject line containing "4472".

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
        response = f.read()
except Exception as e:
    fail(f"Could not read response file: {e}")

if "4472" in response:
    pass_test("Response contains '4472'")
else:
    fail(f"Response does not contain '4472': got '{response.strip()}'")
PYEOF
