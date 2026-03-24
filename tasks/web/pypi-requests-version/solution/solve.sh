#!/bin/bash
# Reference solution for pypi-requests-version.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://pypi.org/pypi/requests/json"
with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

version = data["info"]["version"]
print(version)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(version)
PYEOF
