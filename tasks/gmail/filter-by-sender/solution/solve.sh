#!/bin/bash
# Reference solution for filter-by-sender.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
count = 0
with open("/workspace/inbox.txt", "r") as f:
    for line in f:
        if line.startswith("From:") and "notifications@github.com" in line:
            count += 1

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(str(count))

print(f"Emails from notifications@github.com: {count}")
PYEOF
