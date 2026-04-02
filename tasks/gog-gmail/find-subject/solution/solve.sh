#!/bin/bash
# Reference solution: find the invoice subject line.
mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import json, subprocess

with open("/workspace/test_label.txt") as f:
    label = f.read().strip()

result = subprocess.run(
    ["gog", "gmail", "search", f"label:{label} subject:invoice", "--json"],
    capture_output=True, text=True, timeout=30
)
messages = json.loads(result.stdout)
if isinstance(messages, list) and messages:
    subject = messages[0].get("subject", "")
    # Strip the label prefix
    prefix = f"[{label}] "
    if subject.startswith(prefix):
        subject = subject[len(prefix):]
    with open("/workspace/.logs/agent/response.txt", "w") as f:
        f.write(subject)
    print(f"Found: {subject}")
PYEOF
