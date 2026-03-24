#!/bin/bash
# Reference solution for flask-github-language.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/repos/pallets/flask"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

language = data.get("language", "Python")
print(language)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(language)
PYEOF
