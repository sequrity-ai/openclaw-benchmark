#!/bin/bash
# Reference solution for today-high-reykjavik.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os
from datetime import date

today = date.today().isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=64.13&longitude=-21.90"
    "&daily=temperature_2m_max"
    "&timezone=auto"
    f"&start_date={today}&end_date={today}"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

high = data["daily"]["temperature_2m_max"][0]
response = f"{high}"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
