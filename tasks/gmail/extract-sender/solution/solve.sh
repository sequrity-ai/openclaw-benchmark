#!/bin/bash
# Reference solution for extract-sender.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import re

with open("/workspace/email.txt", "r") as f:
    content = f.read()

for line in content.splitlines():
    if line.startswith("From:"):
        # Extract name from "From: Name <email>" format
        match = re.match(r"From:\s+(.+?)\s+<", line)
        if match:
            name = match.group(1).strip()
        else:
            name = line[5:].strip()
        break

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(name)

print(f"Sender: {name}")
PYEOF
