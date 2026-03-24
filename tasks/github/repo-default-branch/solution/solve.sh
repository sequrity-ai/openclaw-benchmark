#!/bin/bash
# Reference solution for repo-default-branch.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/repos/rust-lang/rust"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

branch = data["default_branch"]
print(branch)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(branch)
PYEOF
