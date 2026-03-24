#!/bin/bash
# Test: aggregate-and-report
# Check that spending_report.txt exists, contains "housing" and "2750" (case-insensitive)

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

report_file = "/workspace/spending_report.txt"
try:
    with open(report_file, "r") as f:
        content = f.read()
except Exception as e:
    fail(f"Could not read {report_file}: {e}")

print(f"spending_report.txt content:\n{content}")
content_lower = content.lower()

if "housing" not in content_lower:
    fail("'housing' not found in spending_report.txt")

if "2750" not in content:
    fail("'2750' not found in spending_report.txt")

pass_test("spending_report.txt contains 'housing' and '2750'")
PYEOF
