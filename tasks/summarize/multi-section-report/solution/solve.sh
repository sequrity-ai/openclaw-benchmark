#!/bin/bash
# Reference solution for multi-section-report.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/report.txt", "r") as f:
    content = f.read()

summary = (
    "NovaTech Ltd's Q1 2026 quarterly report shows strong performance. "
    "Financial highlights: total revenue of $4.2 million, up 18% year-over-year, with gross margin "
    "improving to 67% and EBITDA of $1.3 million (31% growth). "
    "Operational highlights: the company hired 23 new employees, bringing headcount to 187, and "
    "achieved SOC 2 Type II certification. "
    "The Singapore office expansion is on track for a June 1, 2026 opening to serve Asia-Pacific clients. "
    "Q2 2026 revenue guidance is $4.5–4.8 million, with a full-year target of $18 million."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
