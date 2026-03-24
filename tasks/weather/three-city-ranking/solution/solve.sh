#!/bin/bash
# Reference solution for three-city-ranking.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os

cities = {
    "Tokyo":   (35.68, 139.65),
    "Seoul":   (37.57, 126.98),
    "Beijing": (39.90, 116.41),
}

def fetch_max(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max"
        "&timezone=auto"
        "&start_date=2026-02-23&end_date=2026-02-23"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return float(data["daily"]["temperature_2m_max"][0])

temps = {city: fetch_max(lat, lon) for city, (lat, lon) in cities.items()}
ranked = sorted(temps.keys(), key=lambda c: temps[c], reverse=True)

lines = [f"{i+1}. {city}: {temps[city]}°C" for i, city in enumerate(ranked)]
response = "Warmest to coldest: " + ", ".join(f"{city} ({temps[city]}°C)" for city in ranked)
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
