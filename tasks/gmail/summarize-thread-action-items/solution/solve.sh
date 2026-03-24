#!/bin/bash
# Reference solution for summarize-thread-action-items.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
action_items = [
    "Jake will finalize the landing page by April 15",
    "Priya will coordinate with the PR team by April 12",
    "Tom will set up the analytics dashboard by April 18",
]

response = "\n".join(f"- {item}" for item in action_items)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)

print(response)
PYEOF
