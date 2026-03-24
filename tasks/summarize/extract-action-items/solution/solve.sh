#!/bin/bash
# Reference solution for extract-action-items.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
import os

with open("/workspace/project_brief.txt", "r") as f:
    content = f.read()

summary = (
    "Action items and owners from the Nexus Platform v2 project brief:\n\n"
    "1. Bob: Set up CI/CD pipeline by April 5. Includes selecting pipeline tooling, configuring "
    "build caching, and integrating with the secrets management system.\n\n"
    "2. Carol: Conduct user research sessions and deliver findings report by April 10. Will capture "
    "pain points, workflow patterns, and feature requests from 120 internal users.\n\n"
    "3. Dan: Finalize database schema for all seven core services by April 3. This is the critical "
    "path item that Phase 2 service migration depends on.\n\n"
    "4. Eva: Create wireframes for key user flows (developer dashboard and deployment interface) "
    "by April 8, to be reviewed against Carol's user research findings."
)

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(summary)

print(summary)
PYEOF
