#!/bin/bash
# Test: repo-language-breakdown
# Fetch tensorflow/tensorflow languages from GitHub API, check top language (C++) in response.

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
url = "https://api.github.com/repos/tensorflow/tensorflow/languages"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"GitHub API request failed: {e}")

try:
    sorted_langs = sorted(data.items(), key=lambda x: x[1], reverse=True)
    top_lang = sorted_langs[0][0]
    top3 = [lang for lang, _ in sorted_langs[:3]]
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"GitHub API top language: {top_lang}, top 3: {top3}")

response_lower = response.lower()
# Check that the #1 language appears in the response
# C++ may appear as "c++" or "c&#43;&#43;" in HTML-encoded contexts
if top_lang.lower() in response_lower or "c++" in response_lower:
    pass_test(f"Response contains top language '{top_lang}'")
else:
    fail(f"Response does not contain top language '{top_lang}'. Response: {response!r}")
PYEOF
