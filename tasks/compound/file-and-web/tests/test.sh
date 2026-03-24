#!/bin/bash
# Test: file-and-web
# Check that city_countries.txt contains France, Japan, and Australia (case-insensitive)

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

output_file = "/workspace/city_countries.txt"
try:
    with open(output_file, "r") as f:
        content = f.read()
except Exception as e:
    fail(f"Could not read {output_file}: {e}")

content_lower = content.lower()
print(f"city_countries.txt content:\n{content}")

missing = []
for expected in ["france", "japan", "australia"]:
    if expected not in content_lower:
        missing.append(expected)

if missing:
    fail(f"Missing expected countries: {missing}")
else:
    pass_test("Found france, japan, and australia in city_countries.txt")
PYEOF
