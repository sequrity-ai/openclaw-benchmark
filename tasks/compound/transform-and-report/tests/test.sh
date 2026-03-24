#!/bin/bash
# Test: transform-and-report
# Check that widget_total.txt contains "450"

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

total_file = "/workspace/widget_total.txt"
try:
    with open(total_file, "r") as f:
        content = f.read().strip()
except Exception as e:
    fail(f"Could not read {total_file}: {e}")

print(f"widget_total.txt content: {repr(content)}")

numbers = re.findall(r'\d+(?:\.\d+)?', content)
if not numbers:
    fail(f"No number found in widget_total.txt")

total = float(numbers[0])
if abs(total - 450) < 0.01:
    pass_test(f"Widget Pro total is 450")
else:
    fail(f"Expected 450, got {total}")
PYEOF
