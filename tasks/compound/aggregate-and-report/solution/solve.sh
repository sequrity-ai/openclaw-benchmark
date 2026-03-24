#!/bin/bash
# Reference solution for aggregate-and-report.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import csv
import os

totals = {}
with open("/workspace/transactions.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row["category"]
        amount = float(row["amount"])
        totals[category] = totals.get(category, 0) + amount

# Sort by amount descending
sorted_totals = sorted(totals.items(), key=lambda x: x[1], reverse=True)

lines = []
for category, total in sorted_totals:
    lines.append(f"{category}: ${int(total)}")

report = "\n".join(lines) + "\n"

with open("/workspace/spending_report.txt", "w") as f:
    f.write(report)

print(report)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(report)
PYEOF
