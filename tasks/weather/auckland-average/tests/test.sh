#!/bin/bash
# Test: auckland-average
# Fetch 2026-02-22 for Auckland, compute (max+min)/2, check response
# contains a number within ±2°C of the average.

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

# Fetch Auckland 2026-02-22
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-36.85&longitude=174.76"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
    "&start_date=2026-02-22&end_date=2026-02-22"
)

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"API request failed: {e}")

try:
    t_max = float(data["daily"]["temperature_2m_max"][0])
    t_min = float(data["daily"]["temperature_2m_min"][0])
except Exception as e:
    fail(f"Could not parse API response: {e}")

actual_avg = (t_max + t_min) / 2.0
print(f"Auckland 2026-02-22: max={t_max}°C, min={t_min}°C, avg={actual_avg:.2f}°C")

# Extract all numbers from response
numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", response)]
if not numbers:
    fail("No number found in agent response")

print(f"Numbers in response: {numbers}")

if any(abs(n - actual_avg) <= 2.0 for n in numbers):
    closest = min(numbers, key=lambda n: abs(n - actual_avg))
    pass_test(f"Found {closest}°C within ±2°C of actual average {actual_avg:.2f}°C")
else:
    fail(f"No number within ±2°C of actual average {actual_avg:.2f}°C in {numbers}")
PYEOF
