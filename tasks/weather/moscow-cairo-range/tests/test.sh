#!/bin/bash
# Test: moscow-cairo-range
# Fetch 2026-02-23 for Moscow and Cairo.
# Compute |moscow_range - cairo_range| where range = max - min.
# Check that agent's reported number is within ±1°C.

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

def fetch_daily(lat, lon, date_str):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
        "&timezone=auto"
        f"&start_date={date_str}&end_date={date_str}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    t_max = float(data["daily"]["temperature_2m_max"][0])
    t_min = float(data["daily"]["temperature_2m_min"][0])
    return t_max, t_min

try:
    moscow_max, moscow_min = fetch_daily(55.75, 37.62, "2026-02-23")
    cairo_max,  cairo_min  = fetch_daily(30.04, 31.24, "2026-02-23")
except Exception as e:
    fail(f"API request failed: {e}")

moscow_range = moscow_max - moscow_min
cairo_range  = cairo_max  - cairo_min
actual_diff  = abs(moscow_range - cairo_range)

print(f"Moscow 2026-02-23: max={moscow_max}, min={moscow_min}, range={moscow_range:.2f}°C")
print(f"Cairo  2026-02-23: max={cairo_max},  min={cairo_min},  range={cairo_range:.2f}°C")
print(f"Difference of ranges: {actual_diff:.2f}°C")

# Extract all numbers from agent response
numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", response)]
if not numbers:
    fail("No number found in agent response")

print(f"Numbers in response: {numbers}")

if any(abs(n - actual_diff) <= 1.0 for n in numbers):
    closest = min(numbers, key=lambda n: abs(n - actual_diff))
    pass_test(f"Found {closest}°C within ±1°C of actual diff {actual_diff:.2f}°C")
else:
    fail(f"No number within ±1°C of actual diff {actual_diff:.2f}°C in {numbers}")
PYEOF
