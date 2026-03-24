#!/bin/bash
# Reference solution for meeting-notes-summary.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/meeting_notes.txt", "r") as f:
    content = f.read()

summary = (
    "Key decision: The team, led by project lead Alice, voted unanimously to migrate to PostgreSQL "
    "due to its advanced indexing and JSONB storage capabilities. "
    "The project deadline is April 30, 2026. "
    "Action items include Ben preparing a migration script by March 28, Carol updating the API layer "
    "by April 5, David setting up the staging PostgreSQL environment by March 25, and Alice reviewing "
    "the migration plan by March 22."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
