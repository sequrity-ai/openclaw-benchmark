#!/usr/bin/env python3
"""Setup: send 5 emails simulating a product launch coordination thread with action items."""

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
        "subject": "Product Launch Coordination - Action Items Needed",
        "body": (
            "From: Rachel Kim\n\n"
            "Hi team,\n\n"
            "Our product launch is approaching and we need to finalize responsibilities. "
            "Please confirm your tasks and deadlines by replying to this thread.\n\n"
            "Key areas:\n"
            "- Landing page (Jake)\n"
            "- PR and communications (Priya)\n"
            "- Analytics setup (Tom)\n\nRachel"
        ),
    },
    {
        "subject": "Re: Product Launch - Jake's Update",
        "body": (
            "From: Jake Torres\n\n"
            "I will finalize the landing page by April 15. The design is 80% done, "
            "just need to integrate the payment widget and run final QA.\n\nJake"
        ),
    },
    {
        "subject": "Re: Product Launch - Priya's Update",
        "body": (
            "From: Priya Patel\n\n"
            "I will coordinate with the PR team by April 12. Press release draft is ready, "
            "waiting for legal review. Social media calendar is set.\n\nPriya"
        ),
    },
    {
        "subject": "Re: Product Launch - Tom's Update",
        "body": (
            "From: Tom Nakamura\n\n"
            "I will set up the analytics dashboard by April 18. GA4 events are configured, "
            "just need to build the custom dashboard views and set up alerts.\n\nTom"
        ),
    },
    {
        "subject": "Re: Product Launch - Summary from Rachel",
        "body": (
            "From: Rachel Kim\n\n"
            "Great, here is the confirmed action item summary:\n\n"
            "1. Jake Torres: Finalize landing page by April 15\n"
            "2. Priya Patel: Coordinate with PR team by April 12\n"
            "3. Tom Nakamura: Set up analytics dashboard by April 18\n\n"
            "Let me know if anything changes.\n\nRachel"
        ),
    },
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
write_manifest(workspace, label_name, ids, test_email)
