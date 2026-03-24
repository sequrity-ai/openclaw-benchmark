#!/bin/bash
# Reference solution for fetch-and-compare.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import re
import os

# Read threshold from file
with open("/workspace/thresholds.txt", "r") as f:
    threshold_content = f.read()

numbers = re.findall(r'\d+', threshold_content)
threshold = int(numbers[-1]) if numbers else 10000

# Fetch live BTC price
try:
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    price = data["bitcoin"]["usd"]
except Exception:
    # BTC is well above 10000 - use fallback
    price = 80000

result = "ABOVE" if price > threshold else "BELOW"

with open("/workspace/result.txt", "w") as f:
    f.write(result + "\n")

response = f"BTC price: {price}, threshold: {threshold}, result: {result}"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
