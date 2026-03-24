#!/bin/bash
# Reference solution for org-public-repos.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/orgs/django"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

count = data["public_repos"]
response = str(count)
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
