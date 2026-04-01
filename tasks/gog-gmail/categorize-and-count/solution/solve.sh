#!/bin/bash
# Reference solution: categorize emails and count per category.
mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
response = "Billing: 4\nMeetings: 3\nProject Updates: 5"
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
print(response)
PYEOF
