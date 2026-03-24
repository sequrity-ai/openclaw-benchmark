#!/bin/bash
# Reference solution for specific-date-dubai.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=25.27&longitude=55.30"
    "&daily=temperature_2m_max,temperature_2m_min"
    "&timezone=auto"
    "&start_date=2026-02-20&end_date=2026-02-20"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

high = data["daily"]["temperature_2m_max"][0]
low  = data["daily"]["temperature_2m_min"][0]
response = f"High: {high}°C, Low: {low}°C"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
