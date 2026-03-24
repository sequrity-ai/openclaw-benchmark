#!/bin/bash
# Test: fetch-and-compare
# Check that result.txt exists and contains "above" (case-insensitive)
# BTC is always above $10000

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

result_file = "/workspace/result.txt"
try:
    with open(result_file, "r") as f:
        content = f.read().strip()
except Exception as e:
    fail(f"Could not read {result_file}: {e}")

print(f"result.txt content: {repr(content)}")

if "above" in content.lower():
    pass_test(f"result.txt contains 'ABOVE' as expected (BTC > $10000)")
else:
    fail(f"Expected 'ABOVE' in result.txt, got: {repr(content)}")
PYEOF
