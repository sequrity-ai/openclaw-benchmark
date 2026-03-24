#!/bin/bash
# Test: chicago-wind
# Fetch tomorrow's windspeed_10m_max for Chicago from Open-Meteo,
# extract number from agent response, pass if within ±5 km/h.

set -e

python3 - <<'PYEOF'
import sys
import os
import re
import urllib.request
import urllib.error
import json
from datetime import date, timedelta

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

# Fetch tomorrow's wind for Chicago
tomorrow = (date.today() + timedelta(days=1)).isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=41.88&longitude=-87.63"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
    f"&start_date={tomorrow}&end_date={tomorrow}"
)

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"API request failed: {e}")

try:
    actual_wind = float(data["daily"]["windspeed_10m_max"][0])
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"Actual Chicago wind tomorrow: {actual_wind} km/h")

# Extract all numbers from response
numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", response)]
if not numbers:
    fail("No number found in agent response")

print(f"Numbers in response: {numbers}")

if any(abs(n - actual_wind) <= 5.0 for n in numbers):
    closest = min(numbers, key=lambda n: abs(n - actual_wind))
    pass_test(f"Found {closest} km/h within ±5 km/h of actual {actual_wind} km/h")
else:
    fail(f"No number within ±5 km/h of actual wind {actual_wind} km/h in {numbers}")
PYEOF
