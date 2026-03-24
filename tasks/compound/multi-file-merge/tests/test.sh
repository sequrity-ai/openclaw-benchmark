#!/bin/bash
# Test: multi-file-merge
# Check that annual_total.txt contains "403000" or "403,000"

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

total_file = "/workspace/annual_total.txt"
try:
    with open(total_file, "r") as f:
        content = f.read().strip()
except Exception as e:
    fail(f"Could not read {total_file}: {e}")

print(f"annual_total.txt content: {repr(content)}")

# Accept 403000 or 403,000
content_normalized = content.replace(",", "")
numbers = re.findall(r'\d+', content_normalized)
if not numbers:
    fail(f"No number found in annual_total.txt")

# Find 403000 specifically
found_403000 = any(int(n) == 403000 for n in numbers if len(n) <= 7)
if found_403000:
    pass_test("Found 403000 in annual_total.txt")
else:
    fail(f"Expected 403000, found numbers: {numbers}")
PYEOF
