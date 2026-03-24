#!/bin/bash
# Test: user-public-repos
# Fetch torvalds user from GitHub API, check public_repos count within ±3.

set -e

python3 - <<'PYEOF'
import sys
import os
import re
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
url = "https://api.github.com/users/torvalds"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"GitHub API request failed: {e}")

try:
    actual = int(data["public_repos"])
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"GitHub API says torvalds public_repos: {actual}")

numbers = [int(x) for x in re.findall(r"\d+", response)]
if not numbers:
    fail("No number found in agent response")

print(f"Numbers in response: {numbers}")

if any(abs(n - actual) <= 3 for n in numbers):
    closest = min(numbers, key=lambda n: abs(n - actual))
    pass_test(f"Found {closest} within ±3 of actual {actual}")
else:
    fail(f"No number within ±3 of actual {actual} in {numbers}")
PYEOF
