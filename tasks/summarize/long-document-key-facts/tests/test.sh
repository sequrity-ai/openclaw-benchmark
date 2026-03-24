#!/bin/bash
# Test: long-document-key-facts
# Check that response mentions QuantumCache and at least one key performance claim.

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

if "quantumcache" not in response:
    fail("Response does not mention 'quantumcache'")

if "99.99" not in response and "millisecond" not in response and "40" not in response:
    fail("Response does not mention any of the key performance claims: '99.99', 'millisecond', or '40'")

pass_test("Response mentions 'quantumcache' and at least one key performance claim")
PYEOF
