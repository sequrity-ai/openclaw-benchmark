#!/bin/bash
# Reference solution for tomorrow-rain-singapore.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os
from datetime import date, timedelta

tomorrow = (date.today() + timedelta(days=1)).isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=1.29&longitude=103.85"
    "&daily=precipitation_sum"
    "&timezone=auto"
    f"&start_date={tomorrow}&end_date={tomorrow}"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

precip = data["daily"]["precipitation_sum"][0]
will_rain = precip > 0.1
answer = "Yes" if will_rain else "No"
response = f"{answer}, expected precipitation: {precip} mm"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
