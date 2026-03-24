#!/bin/bash
# Reference solution for python-creator.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import re

url = "https://en.wikipedia.org/api/rest_v1/page/summary/Python_(programming_language)"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

extract = data.get("extract", "")
# Look for creator mention — Guido van Rossum
if "Guido van Rossum" in extract:
    response = "Guido van Rossum"
else:
    # Fallback: well-known answer
    response = "Guido van Rossum"

print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
