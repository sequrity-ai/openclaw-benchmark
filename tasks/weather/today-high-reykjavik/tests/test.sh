#!/bin/bash
# Test: today-high-reykjavik
# Fetch today's max temp for Reykjavik from Open-Meteo, extract first number
# from agent response, pass if within ±2°C.

set -e

RESPONSE_FILE="/logs/agent/response.txt"

python3 - <<'PYEOF'
import sys
import os
import re
import urllib.request
import urllib.error
import json
from datetime import date

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

# Extract first number (int or float, possibly negative) from response
numbers = re.findall(r"-?\d+(?:\.\d+)?", response)
if not numbers:
    fail("No number found in agent response")

agent_value = float(numbers[0])

# Fetch today's max temp for Reykjavik from Open-Meteo
today = date.today().isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=64.13&longitude=-21.90"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
    f"&start_date={today}&end_date={today}"
)

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"API request failed: {e}")

try:
    actual = float(data["daily"]["temperature_2m_max"][0])
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"Actual high: {actual}°C, Agent reported: {agent_value}°C")

if abs(agent_value - actual) <= 2.0:
    pass_test(f"Within ±2°C tolerance (diff={abs(agent_value - actual):.2f})")
else:
    fail(f"Outside ±2°C tolerance: actual={actual}, agent={agent_value}")
PYEOF
