#!/bin/bash
# Reference solution for compare-two-documents.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/proposal_a.txt", "r") as f:
    content_a = f.read()

with open("/workspace/proposal_b.txt", "r") as f:
    content_b = f.read()

summary = (
    "Comparison of Proposal A (Team Alpha) and Proposal B (Team Beta):\n\n"
    "Cheaper: Proposal B from Team Beta at $35,000, which is $15,000 less than Proposal A's $50,000.\n\n"
    "Faster to deliver: Proposal A from Team Alpha at 3 months, compared to Proposal B's 5 months.\n\n"
    "Summary: Team Alpha (Proposal A) offers faster delivery (3 months, React + Node.js) but at higher cost ($50,000). "
    "Team Beta (Proposal B) is cheaper ($35,000, Django + Vue.js) but takes longer (5 months) with a greater "
    "emphasis on security and documentation. The choice depends on whether speed or cost is the higher priority."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
