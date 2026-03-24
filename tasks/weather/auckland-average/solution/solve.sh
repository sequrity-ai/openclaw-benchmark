#!/bin/bash
# Reference solution for auckland-average.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-36.85&longitude=174.76"
    "&daily=temperature_2m_max,temperature_2m_min"
    "&timezone=auto"
    "&start_date=2026-02-22&end_date=2026-02-22"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

t_max = float(data["daily"]["temperature_2m_max"][0])
t_min = float(data["daily"]["temperature_2m_min"][0])
avg   = (t_max + t_min) / 2.0
response = f"Average temperature: {avg:.1f}°C  (max={t_max}, min={t_min})"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
