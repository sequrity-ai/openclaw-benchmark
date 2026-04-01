#!/usr/bin/env python3
"""Setup: send 5 emails, one with an invoice subject."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
from gog_helper import *

workspace = get_workspace()
os.makedirs(workspace, exist_ok=True)
test_email = get_test_email()
label_name = create_label()

EMAILS = [
    {"subject": "Updated Remote Work Policy - Effective April 1",  "body": "Please review the new remote work policy attached."},
    {"subject": "Invoice #4472 - March Services",                  "body": "Attached is invoice #4472 for March consulting services. Payment due April 15."},
    {"subject": "Security Training Completion Required by March 31","body": "Please complete your annual security training before the deadline."},
    {"subject": "Lunch Meeting Tomorrow at Noon",                   "body": "Let's meet at the cafeteria tomorrow at noon."},
    {"subject": "Tech Digest Weekly - Top Stories in Cloud Computing","body": "This week's top stories in cloud computing and AI."},
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
write_manifest(workspace, label_name, ids, test_email)
