#!/bin/bash
# Reference solution for email-thread-summary.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/email_thread.txt", "r") as f:
    content = f.read()

summary = (
    "The email thread between Sandra, Marcus, and Priya concerns planning for DevSummit 2026. "
    "Key decisions made: the conference will be held June 12-14, 2026, at the Hilton Downtown. "
    "The expected attendance is approximately 500 people. "
    "Priya will send the formal booking request to Hilton Downtown, and Sandra needs to confirm "
    "the final headcount. A call for speakers will be drafted once venue confirmation is received."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
