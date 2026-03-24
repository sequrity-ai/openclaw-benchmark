#!/bin/bash
# Reference solution for requests-pypi-license.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://pypi.org/pypi/requests/json"
with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode())

license_str = data["info"].get("license", "Apache 2.0")
# Normalize to something concise
if not license_str:
    license_str = "Apache 2.0"
print(license_str)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(license_str)
PYEOF
