#!/bin/bash
# Test: specific-date-dubai
# Fetch 2026-02-20 for Dubai from Open-Meteo, find any two numbers in agent
# response matching actual high and low within ±2°C each.

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

# Extract all numbers from response
numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", response)]
if len(numbers) < 2:
    fail(f"Need at least 2 numbers in response, found: {numbers}")

# Fetch Dubai 2026-02-20 from Open-Meteo
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=25.27&longitude=55.30"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
    "&start_date=2026-02-20&end_date=2026-02-20"
)

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"API request failed: {e}")

try:
    actual_high = float(data["daily"]["temperature_2m_max"][0])
    actual_low  = float(data["daily"]["temperature_2m_min"][0])
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"Actual high: {actual_high}°C, actual low: {actual_low}°C")
print(f"Numbers found in response: {numbers}")

# Check whether any pair of numbers from the response matches high and low
high_matched = any(abs(n - actual_high) <= 2.0 for n in numbers)
low_matched  = any(abs(n - actual_low)  <= 2.0 for n in numbers)

if high_matched and low_matched:
    pass_test(f"Both high ({actual_high}) and low ({actual_low}) matched within ±2°C")
elif high_matched:
    fail(f"High matched but low ({actual_low}) not found in {numbers}")
elif low_matched:
    fail(f"Low matched but high ({actual_high}) not found in {numbers}")
else:
    fail(f"Neither high ({actual_high}) nor low ({actual_low}) matched in {numbers}")
PYEOF
