#!/bin/bash
# Teardown for gmail-live/count-unread.
# Deletes all test messages and the test label from Gmail.

set -e

WORKSPACE="${1:-/workspace}"
MANIFEST="$WORKSPACE/.manifest.json"

if [ ! -f "$MANIFEST" ]; then
    echo "No manifest found at $MANIFEST, nothing to clean up."
    exit 0
fi

# Extract message IDs and label from manifest
MESSAGE_IDS=$(python3 -c "
import json, sys
with open('$MANIFEST') as f:
    m = json.load(f)
ids = m.get('message_ids', [])
print(' '.join(ids))
")

LABEL=$(python3 -c "
import json
with open('$MANIFEST') as f:
    m = json.load(f)
print(m.get('label', ''))
")

# Trash messages (uses gmail.modify scope; batch delete requires full mail scope)
if [ -n "$MESSAGE_IDS" ]; then
    echo "Trashing test messages: $MESSAGE_IDS"
    gog gmail trash $MESSAGE_IDS || echo "Warning: failed to trash some messages"
fi

# Delete label
if [ -n "$LABEL" ]; then
    echo "Deleting label: $LABEL"
    gog gmail labels delete "$LABEL" --force || echo "Warning: failed to delete label"
fi

echo "Teardown complete."
