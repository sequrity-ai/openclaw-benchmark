#!/bin/bash
# Reference solution for short-article-summary.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/article.txt", "r") as f:
    content = f.read()

summary = (
    "Acme Corp launched CloudSync Pro on March 15, 2026, a cloud storage and synchronization "
    "platform for small and medium-sized businesses priced at $29/month per user. "
    "The platform supports real-time collaboration, automatic version control, and integration "
    "with popular productivity tools, with a 30-day free trial starting March 22, 2026."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
