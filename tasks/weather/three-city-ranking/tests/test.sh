#!/bin/bash
# Test: three-city-ranking
# Fetch 2026-02-23 highs for Tokyo, Seoul, Beijing.
# Check that the first-ranked city appears before the last-ranked city
# in the agent response (ordered by highest first).

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

response_lower = response.lower()

cities = {
    "tokyo":   (35.68, 139.65),
    "seoul":   (37.57, 126.98),
    "beijing": (39.90, 116.41),
}

def fetch_max(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=auto"
        "&start_date=2026-02-23&end_date=2026-02-23"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return float(data["daily"]["temperature_2m_max"][0])

try:
    temps = {city: fetch_max(lat, lon) for city, (lat, lon) in cities.items()}
except Exception as e:
    fail(f"API request failed: {e}")

# Sort cities warmest to coldest
ranked = sorted(temps.keys(), key=lambda c: temps[c], reverse=True)
print(f"Ranking (warmest to coldest): {[(c, temps[c]) for c in ranked]}")

warmest = ranked[0]
coldest = ranked[-1]

# Check both appear in response
if warmest not in response_lower:
    fail(f"Warmest city '{warmest}' not found in response")
if coldest not in response_lower:
    fail(f"Coldest city '{coldest}' not found in response")

# Check warmest appears before coldest
pos_warmest = response_lower.index(warmest)
pos_coldest = response_lower.index(coldest)

if pos_warmest < pos_coldest:
    pass_test(
        f"Correct order: {warmest} ({temps[warmest]}°C) before {coldest} ({temps[coldest]}°C)"
    )
else:
    fail(
        f"Wrong order: {warmest} at pos {pos_warmest} should be before "
        f"{coldest} at pos {pos_coldest} in response"
    )
PYEOF
