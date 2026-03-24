#!/bin/bash
# Reference solution for summarize-and-count.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

# Count ERROR lines in log.txt
with open("/workspace/log.txt", "r") as f:
    lines = f.readlines()

error_count = sum(1 for line in lines if " ERROR " in line)

# Write error count
with open("/workspace/error_count.txt", "w") as f:
    f.write(str(error_count) + "\n")

# Write summary
summary = f"The server log contains {error_count} ERROR entries out of {len(lines)} total log lines, indicating multiple system issues including cache failures, database timeouts, and storage errors."
with open("/workspace/summary.txt", "w") as f:
    f.write(summary + "\n")

response = f"Error count: {error_count}\nSummary: {summary}"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
