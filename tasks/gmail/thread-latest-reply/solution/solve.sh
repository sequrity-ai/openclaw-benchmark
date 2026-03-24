#!/bin/bash
# Reference solution for thread-latest-reply.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import re

with open("/workspace/thread.txt", "r") as f:
    content = f.read()

# Split thread by separator
messages = content.split("\n---\n")

# Get last non-empty message
last_message = messages[-1].strip()

# Extract sender name
sender = None
decision = None
for line in last_message.splitlines():
    if line.startswith("From:"):
        match = re.match(r"From:\s+(.+?)\s+<", line)
        if match:
            sender = match.group(1).strip()
        break

# Find the decision line
for line in last_message.splitlines():
    if "option b" in line.lower():
        decision = line.strip()
        break

response = f"Sender: {sender}\nDecision: {decision}"

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)

print(response)
PYEOF
