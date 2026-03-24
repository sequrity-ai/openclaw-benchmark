#!/bin/bash
# Reference solution for find-subject.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

emails_dir = "/workspace/emails"
invoice_subject = None

for filename in sorted(os.listdir(emails_dir)):
    filepath = os.path.join(emails_dir, filename)
    with open(filepath, "r") as f:
        for line in f:
            if line.startswith("Subject:") and ("invoice" in line.lower() or "#" in line):
                invoice_subject = line[len("Subject:"):].strip()
                break
    if invoice_subject:
        break

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(invoice_subject)

print(f"Invoice subject: {invoice_subject}")
PYEOF
