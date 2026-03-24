#!/bin/bash
# Test: speed-of-light-kms
# Check that agent response contains 299792 (speed of light in km/s).

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

# Read agent response
try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read().strip()
except Exception as e:
    fail(f"Could not read response file: {e}")

# Extract integers from response (strip commas for formatted numbers like 299,792)
cleaned = response.replace(",", "").replace(" ", "")
numbers = [int(x) for x in re.findall(r"\b(\d+)\b", cleaned)]
print(f"Numbers in response: {numbers}")

# The speed of light is exactly 299792 km/s
target = 299792
if any(abs(n - target) <= 1 for n in numbers):
    match = min(numbers, key=lambda n: abs(n - target))
    pass_test(f"Found {match} — correct speed of light in km/s")
else:
    fail(f"Expected {target} (±1), got numbers: {numbers}")
PYEOF
