#!/bin/bash
# Test: tomorrow-rain-singapore
# Fetch tomorrow's precipitation_sum for Singapore from Open-Meteo.
# If >0.1mm: response must contain "yes" or rain-related word.
# If <=0.1mm: response must contain "no" or no-rain word.
# Also check precipitation amount is mentioned within ±2mm.

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
        response = f.read().lower()
except Exception as e:
    fail(f"Could not read response file: {e}")

# Fetch tomorrow's precip for Singapore
tomorrow = (date.today() + timedelta(days=1)).isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=1.29&longitude=103.85"
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
    precip = float(data["daily"]["precipitation_sum"][0])
except Exception as e:
    fail(f"Could not parse API response: {e}")

print(f"Actual precipitation tomorrow in Singapore: {precip} mm")

will_rain = precip > 0.1

# Check yes/no correctness
rain_words    = ["yes", "rain", "precipitation", "wet", "shower", "drizzle"]
no_rain_words = ["no", "dry", "clear", "sunny", "won't", "will not", "not rain", "no rain"]

if will_rain:
    correct_word_found = any(w in response for w in rain_words)
    if not correct_word_found:
        fail(f"Expected rain acknowledgement (precip={precip}mm) but response says: {response[:200]}")
else:
    correct_word_found = any(w in response for w in no_rain_words)
    if not correct_word_found:
        fail(f"Expected no-rain acknowledgement (precip={precip}mm) but response says: {response[:200]}")

# Check that the precipitation amount is mentioned (within ±2mm)
numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", response)]
amount_ok = any(abs(n - precip) <= 2.0 for n in numbers)
if not amount_ok:
    fail(f"Precipitation amount {precip}mm not found within ±2mm in response numbers: {numbers}")

pass_test(f"Correct rain status ({'rain' if will_rain else 'no rain'}) and amount ~{precip}mm reported")
PYEOF
