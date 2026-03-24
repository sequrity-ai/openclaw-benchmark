#!/bin/bash
# Reference solution for count-unread.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

count = 0
with open("/workspace/inbox.txt", "r") as f:
    for line in f:
        if line.strip() == "Status: unread":
            count += 1

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(str(count))

print(f"Unread emails: {count}")
PYEOF
