#!/bin/bash
# Test: pypi-requests-version
# Fetch live version from PyPI, compare to agent response.

set -e

python3 - <<'PYEOF'
import sys
import os
import re
import urllib.request
import json

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

# Fetch actual version from PyPI
try:
    url = "https://pypi.org/pypi/requests/json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    actual_version = data["info"]["version"]
except Exception as e:
    fail(f"Could not fetch PyPI data: {e}")

print(f"PyPI latest version: {actual_version}")
print(f"Agent response: {response}")

# Check if response contains the version string
if actual_version in response:
    pass_test(f"Response contains correct version {actual_version}")
else:
    fail(f"Expected version {actual_version}, got: {response}")
PYEOF
