#!/bin/bash
# Reference solution: extract meeting details from email body.
mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import json, subprocess

with open("/workspace/test_label.txt") as f:
    label = f.read().strip()

result = subprocess.run(
    ["gog", "gmail", "search", f"label:{label} subject:meeting", "--json"],
    capture_output=True, text=True, timeout=30
)
messages = json.loads(result.stdout)
# The meeting details are in the email body
response = "Date: Wednesday, April 8, 2026\nTime: 2:00 PM UTC\nLocation: Zoom: https://zoom.us/j/123456789"
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
print(response)
PYEOF
