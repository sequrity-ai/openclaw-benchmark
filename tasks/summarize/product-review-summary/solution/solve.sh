#!/bin/bash
# Reference solution for product-review-summary.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/review.txt", "r") as f:
    content = f.read()

summary = (
    "Product: BlueAir X500 Air Purifier. Rating: 4/5 stars. "
    "Pros: exceptionally quiet operation, excellent filter life (8+ months), and responsive air "
    "quality sensor with automatic adjustment. "
    "Cons: high initial cost ($349, significantly more than comparable units), and occasional "
    "app connectivity issues. "
    "Overall verdict: recommended for those who prioritize quiet operation and filter longevity "
    "and are not constrained by the upfront price."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
