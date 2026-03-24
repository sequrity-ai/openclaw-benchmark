#!/bin/bash
# Test: flask-github-language
# Fetch GitHub API for pallets/flask, check primary language matches response.

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

# Fetch GitHub API
try:
    url = "https://api.github.com/repos/pallets/flask"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    actual_language = data.get("language", "")
except Exception as e:
    fail(f"Could not fetch GitHub data: {e}")

print(f"GitHub language: {actual_language}")
print(f"Agent response: {response}")

if actual_language.lower() in response.lower():
    pass_test(f"Response contains correct language: {actual_language}")
else:
    fail(f"Expected language '{actual_language}' not found in response: {response}")
PYEOF
