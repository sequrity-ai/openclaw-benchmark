#!/bin/bash
# Test: filter-and-save
# Check that engineering_team.txt exists and has exactly 5 lines

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

team_file = "/workspace/engineering_team.txt"
try:
    with open(team_file, "r") as f:
        content = f.read()
except Exception as e:
    fail(f"Could not read {team_file}: {e}")

lines = [l.strip() for l in content.strip().splitlines() if l.strip()]
print(f"engineering_team.txt has {len(lines)} non-empty lines: {lines}")

if len(lines) == 5:
    pass_test(f"Found exactly 5 engineers in engineering_team.txt")
else:
    fail(f"Expected 5 engineers, found {len(lines)}: {lines}")
PYEOF
