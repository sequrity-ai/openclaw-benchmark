#!/bin/bash
# Test: categorize-and-count
# Verifies that the agent reports counts 4, 3, 5 and category names billing, meeting, project.

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

try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read()
except Exception as e:
    fail(f"Could not read response file: {e}")

lower = response.lower()

has_billing = "billing" in lower or "invoice" in lower
has_meeting = "meeting" in lower
has_project = "project" in lower
has_4 = bool(re.search(r'\b4\b', response))
has_3 = bool(re.search(r'\b3\b', response))
has_5 = bool(re.search(r'\b5\b', response))

missing = []
if not has_billing:
    missing.append("'billing' or 'invoice'")
if not has_meeting:
    missing.append("'meeting'")
if not has_project:
    missing.append("'project'")
if not has_4:
    missing.append("digit '4'")
if not has_3:
    missing.append("digit '3'")
if not has_5:
    missing.append("digit '5'")

if not missing:
    pass_test("Response contains all required category names and counts (4, 3, 5)")
else:
    fail(f"Response missing: {', '.join(missing)}")
PYEOF
