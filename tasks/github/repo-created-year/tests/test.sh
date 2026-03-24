#!/bin/bash
# Test: repo-created-year
# Fetch torvalds/linux from GitHub API, check created_at year in response.

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
url = "https://api.github.com/repos/torvalds/linux"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"GitHub API request failed: {e}")

try:
    created_at = data["created_at"]
    year = created_at[:4]
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"GitHub API says torvalds/linux created_at: {created_at}, year: {year}")

if year in response:
    pass_test(f"Response contains creation year '{year}'")
else:
    fail(f"Response does not contain year '{year}'. Response: {response!r}")
PYEOF
