#!/bin/bash
# Reference solution for extract-all-attachments.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
attachments = []

with open("/workspace/inbox.txt", "r") as f:
    for line in f:
        if line.startswith("Attachments:"):
            # Parse comma-separated filenames
            items = line[len("Attachments:"):].strip().split(",")
            for item in items:
                name = item.strip()
                if name and name not in attachments:
                    attachments.append(name)

response = "\n".join(attachments)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)

print(response)
PYEOF
