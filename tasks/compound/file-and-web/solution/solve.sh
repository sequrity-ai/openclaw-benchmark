#!/bin/bash
# Reference solution for file-and-web.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

# Read cities file
with open("/workspace/cities.txt", "r") as f:
    cities = [line.strip() for line in f if line.strip()]

# Known stable city-country mappings
country_map = {
    "Paris": "France",
    "Tokyo": "Japan",
    "Sydney": "Australia",
}

lines = []
for city in cities:
    country = country_map.get(city, "Unknown")
    lines.append(f"{city}: {country}")

output = "\n".join(lines) + "\n"

with open("/workspace/city_countries.txt", "w") as f:
    f.write(output)

print(output)
with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(output)
PYEOF
