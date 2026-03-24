#!/bin/bash
# Reference solution for two-city-comparison.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os
from datetime import date

today = date.today().isoformat()

def fetch_max(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max"
        "&timezone=auto"
        f"&start_date={today}&end_date={today}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return float(data["daily"]["temperature_2m_max"][0])

oslo_max     = fetch_max(59.91, 10.75)
helsinki_max = fetch_max(60.17, 24.94)

if oslo_max >= helsinki_max:
    response = f"Oslo is warmer: {oslo_max}°C vs Helsinki: {helsinki_max}°C"
else:
    response = f"Helsinki is warmer: {helsinki_max}°C vs Oslo: {oslo_max}°C"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
