#!/bin/bash
# Test: repo-description
# Fetch pallets/flask from GitHub API, check description contains "web" and "framework".

set -e

python3 - <<'PYEOF'
import sys
import os
import urllib.request
import urllib.error
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
        response = f.read()
except Exception as e:
    fail(f"Could not read response file: {e}")

# Fetch ground truth from GitHub API
url = "https://api.github.com/repos/pallets/flask"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"GitHub API request failed: {e}")

try:
    description = data["description"]
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"GitHub API description: {description!r}")

response_lower = response.lower()
if "web" in response_lower and "framework" in response_lower:
    pass_test(f"Response contains 'web' and 'framework'")
else:
    fail(f"Response does not contain both 'web' and 'framework'. Response: {response!r}")
PYEOF
