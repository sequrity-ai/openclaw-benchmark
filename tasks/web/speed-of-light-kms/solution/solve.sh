#!/bin/bash
# Reference solution for speed-of-light-kms.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
# Speed of light in vacuum is exactly 299,792,458 m/s = 299,792.458 km/s
# Rounded to integer: 299792 km/s
response = "299792"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
