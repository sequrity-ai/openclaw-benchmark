#!/bin/bash
# Reference solution for extract-meeting-details.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import re

with open("/workspace/meeting_invite.txt", "r") as f:
    content = f.read()

date_time = None
location = None

for line in content.splitlines():
    if "Meeting Date" in line or ("Date & Time" in line):
        date_time = line.strip()
    if line.startswith("Location:"):
        location = line.strip()

response = f"{date_time}\n{location}"

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)

print(response)
PYEOF
