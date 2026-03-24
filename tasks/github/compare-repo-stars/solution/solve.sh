#!/bin/bash
# Reference solution for compare-repo-stars.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json

def get_stars(owner_repo):
    url = f"https://api.github.com/repos/{owner_repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-bench/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data["stargazers_count"]

react_stars = get_stars("facebook/react")
vue_stars = get_stars("vuejs/vue")

if react_stars > vue_stars:
    winner = "facebook/react"
else:
    winner = "vuejs/vue"

response = (
    f"{winner} has more stars.\n"
    f"facebook/react: {react_stars} stars\n"
    f"vuejs/vue: {vue_stars} stars"
)
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
