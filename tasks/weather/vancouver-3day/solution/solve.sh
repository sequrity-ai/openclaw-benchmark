#!/bin/bash
# Reference solution for vancouver-3day.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os
from datetime import date, timedelta

today     = date.today()
day_after = today + timedelta(days=2)

url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=49.28&longitude=-123.12"
    "&daily=temperature_2m_max"
    "&timezone=auto"
    f"&start_date={today.isoformat()}&end_date={day_after.isoformat()}"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

dates     = data["daily"]["time"]
max_temps = [float(t) for t in data["daily"]["temperature_2m_max"]]
best_idx  = max_temps.index(max(max_temps))
labels    = ["today", "tomorrow", "day after tomorrow"]
response  = f"The warmest day is {labels[best_idx]} ({dates[best_idx]}) with a high of {max_temps[best_idx]}°C"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
