#!/bin/bash
# Test: categorize-and-count — must mention categories and counts 4, 3, 5
set -e

python3 - <<'PYEOF'
import sys, os, re

reward_dir = os.environ.get("REWARD_DIR", "/tmp")
reward_file = os.path.join(reward_dir, "reward.txt")

def fail(reason=""):
    print(f"FAIL: {reason}", file=sys.stderr)
    with open(reward_file, "w") as f: f.write("0")
    sys.exit(0)

def pass_test(reason=""):
    print(f"PASS: {reason}")
    with open(reward_file, "w") as f: f.write("1")
    sys.exit(0)

try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read().lower()
except Exception as e:
    fail(f"Could not read response file: {e}")

missing = []
# Check category names
if "billing" not in response and "invoice" not in response:
    missing.append("'billing'")
if "meeting" not in response:
    missing.append("'meeting'")
if "project" not in response:
    missing.append("'project'")
# Check counts
if not re.search(r'\b4\b', response):
    missing.append("count '4'")
if not re.search(r'\b3\b', response):
    missing.append("count '3'")
if not re.search(r'\b5\b', response):
    missing.append("count '5'")

if not missing:
    pass_test("Response contains all categories and counts")
else:
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
