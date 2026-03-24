#!/bin/bash
# Reference solution for eiffel-tower-height.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import re

url = "https://en.wikipedia.org/api/rest_v1/page/summary/Eiffel_Tower"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

extract = data.get("extract", "")
# Look for height patterns like "330 m"
matches = re.findall(r"(\d{3}(?:\.\d+)?)\s*(?:m\b|metres?\b|meters?\b)", extract, re.IGNORECASE)
candidates = [m for m in matches if 300 <= float(m) <= 400]

if candidates:
    height = candidates[0]
else:
    # Known height of Eiffel Tower to tip
    height = "330"

print(height)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(height)
PYEOF
