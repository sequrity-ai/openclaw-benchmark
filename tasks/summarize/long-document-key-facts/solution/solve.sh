#!/bin/bash
# Reference solution for long-document-key-facts.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/whitepaper.txt", "r") as f:
    content = f.read()

summary = (
    "Top 3 performance claims about QuantumCache from the whitepaper:\n\n"
    "1. Sub-millisecond latency: QuantumCache achieves sub-millisecond read latency at the 99th "
    "percentile (p99 = 0.74 ms at 500,000 ops/sec), compared to 2.3 ms for Redis — a 3x improvement.\n\n"
    "2. 99.99% uptime: Over a 12-month measured period across all production deployments, QuantumCache "
    "achieved 99.99% uptime, corresponding to less than 53 minutes of cumulative downtime per year.\n\n"
    "3. 40% cost reduction at TechGiant Inc: Replacing Redis with QuantumCache for their e-commerce "
    "product recommendation engine resulted in a 40% infrastructure cost reduction, with average "
    "recommendation latency dropping from 4.2 ms to 0.9 ms."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
