#!/bin/bash
# Reference solution for web-to-file.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

# Tokyo metropolitan area population is approximately 13.96 million (stable well-known value)
population = 13.96

with open("/workspace/tokyo_population.txt", "w") as f:
    f.write(f"{population}\n")

response = f"Tokyo population: {population} million"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
