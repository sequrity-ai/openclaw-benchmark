#!/bin/bash
# Test: mars-moon-count
# Check that agent reports Mars has 2 moons.

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
        response = f.read()
except Exception as e:
    fail(f"Could not read response file: {e}")

# Extract integers from response
numbers = [int(x) for x in re.findall(r"\b(\d+)\b", response)]
if not numbers:
    fail("No integer found in agent response")

print(f"Numbers in response: {numbers}")

if any(n == 2 for n in numbers):
    pass_test("Found 2 (correct number of Mars moons: Phobos and Deimos)")
else:
    fail(f"Expected 2 moons, got numbers: {numbers}")
PYEOF
