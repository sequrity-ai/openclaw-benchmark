#!/bin/bash
# Reference solution for repo-created-year.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/repos/torvalds/linux"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

created_at = data["created_at"]
year = created_at[:4]
print(year)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(year)
PYEOF
