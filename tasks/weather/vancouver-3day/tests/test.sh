#!/bin/bash
# Test: vancouver-3day
# Fetch 3-day forecast for Vancouver, find the warmest day, check response
# contains the correct date (YYYY-MM-DD) or day name (today/tomorrow/day after tomorrow).

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

response_lower = response.lower()

# Build 3-day date range
today     = date.today()
tomorrow  = today + timedelta(days=1)
day_after = today + timedelta(days=2)

start = today.isoformat()
end   = day_after.isoformat()

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=49.28&longitude=-123.12"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
    f"&start_date={start}&end_date={end}"
)

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
except Exception as e:
    fail(f"API request failed: {e}")

try:
    dates    = data["daily"]["time"]
    max_temps = [float(t) for t in data["daily"]["temperature_2m_max"]]
except Exception as e:
    fail(f"Could not parse API response: {e}")

if len(max_temps) < 3:
    fail(f"Expected 3 days of data, got {len(max_temps)}")

# Find the index of the warmest day
warmest_idx = max_temps.index(max(max_temps))
warmest_date = dates[warmest_idx]

day_labels = {
    0: ["today"],
    1: ["tomorrow"],
    2: ["day after tomorrow", "day-after-tomorrow", "after tomorrow"],
}

print(f"Forecast: {list(zip(dates, max_temps))}")
print(f"Warmest day: {warmest_date} ({max_temps[warmest_idx]}°C) = index {warmest_idx}")

# Check if the correct date string appears
if warmest_date in response:
    pass_test(f"Correct date {warmest_date} found in response")

# Check if the correct day label appears
for label in day_labels.get(warmest_idx, []):
    if label in response_lower:
        pass_test(f"Correct day label '{label}' found in response")

# Build the month/day form too (e.g. "March 22" or "22 March")
dt = date.fromisoformat(warmest_date)
month_name = dt.strftime("%B").lower()
day_num    = str(dt.day)
# e.g. "march 22" or "22 march"
if (f"{month_name} {day_num}" in response_lower or
        f"{day_num} {month_name}" in response_lower):
    pass_test(f"Correct date in month-name form found in response")

fail(
    f"Correct warmest day '{warmest_date}' (idx={warmest_idx}) not found in response. "
    f"Response snippet: {response[:300]}"
)
PYEOF
