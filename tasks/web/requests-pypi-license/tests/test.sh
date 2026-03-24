#!/bin/bash
# Test: requests-pypi-license
# Check that agent response contains "apache" (case-insensitive).

set -e

python3 - <<'PYEOF'
import sys
import os
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

print(f"Agent response: {response}")

# Verify PyPI license field contains "apache"
try:
    url = "https://pypi.org/pypi/requests/json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    pypi_license = data["info"].get("license", "")
    print(f"PyPI license field: {pypi_license}")
except Exception as e:
    print(f"PyPI fetch failed, using fallback check: {e}", file=sys.stderr)
    pypi_license = "Apache 2.0"

# Check response contains "apache" (case-insensitive)
if "apache" in response.lower():
    pass_test(f"Response contains 'apache' — correct license")
else:
    fail(f"Response does not contain 'apache': {response}")
PYEOF
