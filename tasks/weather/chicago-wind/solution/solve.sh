#!/bin/bash
# Reference solution for chicago-wind.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os
from datetime import date, timedelta

tomorrow = (date.today() + timedelta(days=1)).isoformat()
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=41.88&longitude=-87.63"
    "&daily=windspeed_10m_max"
    "&timezone=auto"
    f"&start_date={tomorrow}&end_date={tomorrow}"
)

with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

wind = data["daily"]["windspeed_10m_max"][0]
response = f"Max wind speed tomorrow in Chicago: {wind} km/h"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
