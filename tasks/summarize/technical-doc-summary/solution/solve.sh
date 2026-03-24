#!/bin/bash
# Reference solution for technical-doc-summary.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/api_docs.txt", "r") as f:
    content = f.read()

summary = (
    "The DataStream API v2.3 is a real-time data ingestion and streaming API supporting endpoints "
    "for starting (/stream/start), stopping (/stream/stop), checking status (/stream/status), and "
    "publishing data (/stream/publish). "
    "Authentication uses Bearer tokens that expire after 24 hours. "
    "Key limitations include a rate limit of 1000 requests/hour for standard tier users and a "
    "maximum payload size of 1 MB per publish request. "
    "Version 2.3 improvements include 35% reduced latency on /stream/start, LZ4 compression support, "
    "and expanded geographic availability to 12 new regions."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
