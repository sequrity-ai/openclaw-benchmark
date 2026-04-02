#!/usr/bin/env python3
"""Setup: send 8 emails, mark 3 as unread."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
from gog_helper import *

workspace = get_workspace()
os.makedirs(workspace, exist_ok=True)
test_email = get_test_email()
label_name = create_label()

EMAILS = [
    {"subject": "Q1 Budget Review",            "body": "Please find attached the Q1 budget review.", "unread": False},
    {"subject": "Re: Project Phoenix Timeline", "body": "The timeline looks good to me.",              "unread": True},
    {"subject": "PR #42 opened by jsmith",      "body": "jsmith opened pull request #42.",             "unread": False},
    {"subject": "Performance Reviews",          "body": "Please complete your self-assessment.",       "unread": True},
    {"subject": "Partnership Agreement Draft",  "body": "Please review sections 3 and 7.",            "unread": False},
    {"subject": "Scheduled Maintenance",        "body": "Maintenance on March 20 from 2-4 AM UTC.",   "unread": False},
    {"subject": "Brand Guidelines Released",    "body": "Updated brand guidelines on the intranet.",  "unread": False},
    {"subject": "Expense Report Reminder",      "body": "Submit your February expense report.",        "unread": True},
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
mark_read_unread(ids, EMAILS, label_name)

expected_unread = sum(1 for e in EMAILS if e["unread"])
write_manifest(workspace, label_name, ids, test_email, expected_unread=expected_unread)
print(f"Label: {label_name}, Expected unread: {expected_unread}")
