#!/bin/bash
# Test: eiffel-tower-height
# Fetch Wikipedia summary for Eiffel Tower, extract height, check agent response.

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

# Try to get actual height from Wikipedia as ground truth
actual_height = None
try:
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/Eiffel_Tower"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    extract = data.get("extract", "")
    # Look for height patterns like "330 m" or "330.0 m" or "330-metre"
    matches = re.findall(r"(\d{3}(?:\.\d+)?)\s*(?:m\b|metres?\b|meters?\b)", extract, re.IGNORECASE)
    candidates = [float(m) for m in matches if 300 <= float(m) <= 400]
    if candidates:
        actual_height = candidates[0]
        print(f"Wikipedia height: {actual_height} m")
except Exception as e:
    print(f"Wikipedia fetch failed: {e}", file=sys.stderr)

# Extract numbers from agent response
numbers = [float(x) for x in re.findall(r"\b(\d{3}(?:\.\d+)?)\b", response)]
print(f"Numbers in response: {numbers}")

if actual_height is not None:
    # Check within ±5m of Wikipedia value
    if any(abs(n - actual_height) <= 5.0 for n in numbers):
        closest = min(numbers, key=lambda n: abs(n - actual_height))
        pass_test(f"Found {closest} within ±5m of Wikipedia value {actual_height}")
    else:
        # Fallback: accept 324-335 range
        if any(324 <= n <= 335 for n in numbers):
            pass_test(f"Found number in accepted range 324-335m")
        else:
            fail(f"No number within ±5m of {actual_height} or in range 324-335 in {numbers}")
else:
    # Fallback: accept 324-335 range
    if any(324 <= n <= 335 for n in numbers):
        pass_test(f"Found number in accepted range 324-335m")
    else:
        fail(f"No number in accepted range 324-335 in response: {numbers}")
PYEOF
