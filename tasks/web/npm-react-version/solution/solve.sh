#!/bin/bash
# Reference solution for npm-react-version.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://registry.npmjs.org/react/latest"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

version = data["version"]
print(version)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(version)
PYEOF
