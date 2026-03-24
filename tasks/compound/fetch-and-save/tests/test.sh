#!/bin/bash
# Test: fetch-and-save
# Check that /workspace/btc_price.txt exists and contains a number > 1000

set -e

python3 - <<'PYEOF'
import sys
import os
import re

reward_dir = os.environ.get("REWARD_DIR", "/tmp")
reward_file = os.path.join(reward_dir, "reward.txt")

def fail(reason=""):
    print(f"FAIL: {reason}", file=sys.stderr)
    with open(reward_file, "w") as f:
        f.write("0")
    sys.exit(0)

def pass_test(reason=""):
    print(f"PASS: {reason}")
    with open(reward_file, "w") as f:
        f.write("1")
    sys.exit(0)

# Check btc_price.txt exists
price_file = "/workspace/btc_price.txt"
try:
    with open(price_file, "r") as f:
        content = f.read().strip()
except Exception as e:
    fail(f"Could not read {price_file}: {e}")

# Extract number from file
numbers = re.findall(r'\d+(?:\.\d+)?', content)
if not numbers:
    fail(f"No number found in btc_price.txt, content: {repr(content)}")

price = float(numbers[0])
print(f"Found BTC price: {price}")

if price > 1000:
    pass_test(f"BTC price {price} is greater than 1000")
else:
    fail(f"BTC price {price} is not greater than 1000")
PYEOF
