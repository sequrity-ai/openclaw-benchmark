#!/bin/bash
# Reference solution for repo-primary-language.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/repos/microsoft/vscode"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

language = data["language"]
print(language)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(language)
PYEOF
