#!/bin/bash
# Test: npm-react-version
# Fetch live version from npm registry, compare to agent response.

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

# Fetch actual version from npm registry
try:
    url = "https://registry.npmjs.org/react/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    actual_version = data["version"]
except Exception as e:
    fail(f"Could not fetch npm data: {e}")

print(f"npm latest react version: {actual_version}")
print(f"Agent response: {response}")

# Check if response contains the version string
if actual_version in response:
    pass_test(f"Response contains correct version {actual_version}")
else:
    fail(f"Expected version {actual_version}, got: {response}")
PYEOF
