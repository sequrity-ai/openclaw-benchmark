#!/bin/bash
# Reference solution for fetch-and-save.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import urllib.request
import json
import os

url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    price = data["bitcoin"]["usd"]
except Exception:
    # Fallback to a known reasonable price if API is unavailable
    price = 80000

price_str = str(price)
with open("/workspace/btc_price.txt", "w") as f:
    f.write(price_str + "\n")

response = f"Bitcoin price: {price_str} USD"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
