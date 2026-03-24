#!/bin/bash
# Test: compare-repo-stars
# Fetch facebook/react and vuejs/vue from GitHub API, check response names react as winner.

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
def get_stars(owner_repo):
    url = f"https://api.github.com/repos/{owner_repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data["stargazers_count"]

try:
    react_stars = get_stars("facebook/react")
    vue_stars = get_stars("vuejs/vue")
except Exception as e:
    fail(f"GitHub API request failed: {e}")

if react_stars > vue_stars:
    winner = "react"
else:
    winner = "vue"

print(f"GitHub API: react={react_stars} stars, vue={vue_stars} stars, winner={winner}")

if winner.lower() in response.lower():
    pass_test(f"Response correctly identifies '{winner}' as having more stars")
else:
    fail(f"Response does not mention winner '{winner}'. Response: {response!r}")
PYEOF
