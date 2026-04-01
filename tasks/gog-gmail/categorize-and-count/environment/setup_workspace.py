#!/usr/bin/env python3
"""Setup: send 12 emails across 3 categories (Billing: 4, Meetings: 3, Project Updates: 5)."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
from gog_helper import *

workspace = get_workspace()
os.makedirs(workspace, exist_ok=True)
test_email = get_test_email()
label_name = create_label()

EMAILS = [
    # Billing (4)
    {"subject": "Invoice #1101 - January Services",       "body": "Please find attached invoice #1101 for January services. Payment due Feb 15."},
    {"subject": "Invoice #1187 Overdue Notice",           "body": "Invoice #1187 is now 30 days overdue. Please remit payment immediately."},
    {"subject": "Monthly Subscription Invoice - March",    "body": "Your monthly subscription invoice for March is ready for review."},
    {"subject": "Contractor Invoice #2034 - Q1 Work",     "body": "Attached is the contractor invoice #2034 for Q1 deliverables."},
    # Meetings (3)
    {"subject": "Q2 Planning Meeting - April 5",           "body": "Please join us for the Q2 planning meeting on April 5 at 10 AM."},
    {"subject": "Town Hall Meeting Invite - March 28",     "body": "You are invited to the company town hall meeting on March 28."},
    {"subject": "1:1 Meeting Reschedule - Moving to Thursday","body": "I need to reschedule our 1:1 meeting to Thursday at 3 PM."},
    # Project Updates (5)
    {"subject": "Project Phoenix Backend API Progress",    "body": "Sprint 4 complete. Backend API endpoints 80% done. On track for April release."},
    {"subject": "Homepage Redesign Project Kickoff",       "body": "Kicking off the homepage redesign project. Design phase starts next week."},
    {"subject": "Product Launch Campaign Status",          "body": "Campaign materials 60% complete. Social media assets due by March 25."},
    {"subject": "Mobile App Refactor Sprint 5 Progress",   "body": "Sprint 5 completed. Core navigation refactor done. Performance improved 40%."},
    {"subject": "Dashboard Migration Project Milestone 2", "body": "Milestone 2 reached. Data migration scripts tested. Moving to UAT next week."},
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
write_manifest(workspace, label_name, ids, test_email,
               expected_billing=4, expected_meetings=3, expected_project_updates=5)
