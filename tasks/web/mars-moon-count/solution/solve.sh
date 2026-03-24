#!/bin/bash
# Reference solution for mars-moon-count.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://en.wikipedia.org/api/rest_v1/page/summary/Mars"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

extract = data.get("extract", "")
# Mars has two moons: Phobos and Deimos
response = "2"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
