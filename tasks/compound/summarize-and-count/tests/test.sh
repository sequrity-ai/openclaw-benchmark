#!/bin/bash
# Test: summarize-and-count
# Check error_count.txt contains "12" and summary.txt exists

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

# Check error_count.txt
count_file = "/workspace/error_count.txt"
try:
    with open(count_file, "r") as f:
        count_content = f.read().strip()
except Exception as e:
    fail(f"Could not read {count_file}: {e}")

# Extract number from count file
numbers = re.findall(r'\d+', count_content)
if not numbers:
    fail(f"No number in error_count.txt, content: {repr(count_content)}")

count = int(numbers[0])
print(f"Found error count: {count}")

if count != 12:
    fail(f"Expected error count 12, got {count}")

# Check summary.txt exists and is non-empty
summary_file = "/workspace/summary.txt"
try:
    with open(summary_file, "r") as f:
        summary = f.read().strip()
except Exception as e:
    fail(f"Could not read {summary_file}: {e}")

if not summary:
    fail("summary.txt is empty")

print(f"Summary: {summary}")
pass_test(f"error_count=12 and summary.txt exists ({len(summary)} chars)")
PYEOF
