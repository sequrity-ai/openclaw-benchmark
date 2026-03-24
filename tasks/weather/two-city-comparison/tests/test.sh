#!/bin/bash
# Test: two-city-comparison
# Fetch today's max temp for Oslo and Helsinki, check that the correct
# warmer city name appears in the agent response.

set -e

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

response_lower = response.lower()

today = date.today().isoformat()

def fetch_max(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=auto"
        f"&start_date={today}&end_date={today}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return float(data["daily"]["temperature_2m_max"][0])

try:
    oslo_max    = fetch_max(59.91, 10.75)
    helsinki_max = fetch_max(60.17, 24.94)
except Exception as e:
    fail(f"API request failed: {e}")

print(f"Oslo max: {oslo_max}°C, Helsinki max: {helsinki_max}°C")

# Determine correct winner
if oslo_max > helsinki_max:
    correct_city   = "oslo"
    incorrect_city = "helsinki"
elif helsinki_max > oslo_max:
    correct_city   = "helsinki"
    incorrect_city = "oslo"
else:
    # Tie: accept either city
    if "oslo" in response_lower or "helsinki" in response_lower:
        pass_test("Tie in temperatures; any city name accepted")
    else:
        fail("Tie in temperatures but no city name found in response")

if correct_city in response_lower:
    pass_test(f"{correct_city.title()} correctly identified as warmer ({max(oslo_max, helsinki_max)}°C vs {min(oslo_max, helsinki_max)}°C)")
else:
    fail(f"Expected '{correct_city.title()}' in response but not found. Response: {response[:300]}")
PYEOF
