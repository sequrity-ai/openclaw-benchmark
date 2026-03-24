#!/bin/bash
# Reference solution for moscow-cairo-range.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os

def fetch_daily(lat, lon, date_str):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=auto"
        f"&start_date={date_str}&end_date={date_str}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    t_max = float(data["daily"]["temperature_2m_max"][0])
    t_min = float(data["daily"]["temperature_2m_min"][0])
    return t_max, t_min

moscow_max, moscow_min = fetch_daily(55.75, 37.62, "2026-02-23")
cairo_max,  cairo_min  = fetch_daily(30.04, 31.24, "2026-02-23")

moscow_range = moscow_max - moscow_min
cairo_range  = cairo_max  - cairo_min
diff         = abs(moscow_range - cairo_range)

response = f"Moscow range: {moscow_range:.1f}°C, Cairo range: {cairo_range:.1f}°C, Difference: {diff:.1f}°C"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
