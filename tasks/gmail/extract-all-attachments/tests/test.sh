#!/bin/bash
# Test: extract-all-attachments
# Verifies that the agent lists all 4 unique attachment filenames.

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
        response = f.read()
except Exception as e:
    fail(f"Could not read response file: {e}")

required = ["report.pdf", "budget_2026.xlsx", "logo.png", "presentation.pptx"]
missing = [name for name in required if name not in response]

if not missing:
    pass_test("Response contains all 4 attachment filenames")
else:
    fail(f"Response missing attachments: {missing}")
PYEOF
