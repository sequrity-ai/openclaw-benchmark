#!/bin/bash
# Test: python-creator
# Check that agent response contains "Guido" and "Rossum" (case-insensitive).

set -e

python3 - <<'PYEOF'
import sys
import os

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

# Read agent response
try:
    with open("/logs/agent/response.txt", "r") as f:
        response = f.read().strip()
except Exception as e:
    fail(f"Could not read response file: {e}")

print(f"Agent response: {response}")

response_lower = response.lower()
has_guido = "guido" in response_lower
has_rossum = "rossum" in response_lower

if has_guido and has_rossum:
    pass_test("Response contains 'Guido' and 'Rossum' — correct creator of Python")
elif has_guido:
    fail("Response contains 'Guido' but not 'Rossum'")
elif has_rossum:
    fail("Response contains 'Rossum' but not 'Guido'")
else:
    fail(f"Response does not contain 'Guido' or 'Rossum': {response}")
PYEOF
