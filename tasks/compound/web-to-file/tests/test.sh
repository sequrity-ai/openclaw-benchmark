#!/bin/bash
# Test: web-to-file
# Check that /workspace/tokyo_population.txt exists and contains a number between 9 and 15

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

pop_file = "/workspace/tokyo_population.txt"
try:
    with open(pop_file, "r") as f:
        content = f.read().strip()
except Exception as e:
    fail(f"Could not read {pop_file}: {e}")

numbers = re.findall(r'\d+(?:\.\d+)?', content)
if not numbers:
    fail(f"No number found in tokyo_population.txt, content: {repr(content)}")

pop = float(numbers[0])
print(f"Found Tokyo population: {pop} million")

if 9.0 <= pop <= 15.0:
    pass_test(f"Tokyo population {pop}M is within expected range [9, 15]")
else:
    fail(f"Tokyo population {pop}M is outside expected range [9, 15]")
PYEOF
