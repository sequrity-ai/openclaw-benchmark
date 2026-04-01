#!/usr/bin/env python3
"""Setup: send a meeting invite email."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
from gog_helper import *

workspace = get_workspace()
os.makedirs(workspace, exist_ok=True)
test_email = get_test_email()
label_name = create_label()

EMAILS = [
    {
        "subject": "Q2 Product Strategy Meeting - Calendar Invite",
        "body": (
            "You are invited to the Q2 Product Strategy Meeting.\n\n"
            "Meeting Date: Wednesday, April 8, 2026\n"
            "Time: 2:00 PM UTC\n"
            "Duration: 90 minutes\n"
            "Location: Zoom: https://zoom.us/j/123456789\n\n"
            "Agenda:\n"
            "1. Q1 performance review (20 min)\n"
            "2. Q2 product roadmap discussion (30 min)\n"
            "3. Resource allocation (20 min)\n"
            "4. Open discussion (20 min)\n\n"
            "Please confirm your attendance by replying to this email."
        ),
    },
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
write_manifest(workspace, label_name, ids, test_email)
