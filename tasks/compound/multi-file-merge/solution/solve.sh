#!/bin/bash
# Reference solution for multi-file-merge.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os
import re

total = 0
for filename in ["q1.txt", "q2.txt", "q3.txt"]:
    filepath = os.path.join("/workspace", filename)
    with open(filepath, "r") as f:
        content = f.read()
    numbers = re.findall(r'\d+', content)
    if numbers:
        total += int(numbers[-1])

with open("/workspace/annual_total.txt", "w") as f:
    f.write(str(total) + "\n")

response = f"Annual revenue total: {total}"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
