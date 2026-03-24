#!/bin/bash
# Reference solution for transform-and-report.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import csv
import os

total = 0
with open("/workspace/sales.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["product"] == "Widget Pro":
            total += float(row["amount"])

total = int(total)

with open("/workspace/widget_total.txt", "w") as f:
    f.write(str(total) + "\n")

response = f"Widget Pro total sales: {total}"
print(response)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)
PYEOF
