#!/bin/bash
# Reference solution for repo-language-breakdown.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

url = "https://api.github.com/repos/tensorflow/tensorflow/languages"
req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())

# Sort languages by bytes descending
sorted_langs = sorted(data.items(), key=lambda x: x[1], reverse=True)
top3 = sorted_langs[:3]

lines = []
for i, (lang, bytes_count) in enumerate(top3, 1):
    lines.append(f"{i}. {lang}: {bytes_count} bytes")

response = "\n".join(lines)
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
