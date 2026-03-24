#!/bin/bash
# Reference solution for filter-and-save.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import csv
import os

engineers = []
with open("/workspace/employees.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["department"] == "Engineering":
            engineers.append(row["name"])

with open("/workspace/engineering_team.txt", "w") as f:
    for name in engineers:
        f.write(name + "\n")

response = f"Engineering team ({len(engineers)} members):\n" + "\n".join(engineers)
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
