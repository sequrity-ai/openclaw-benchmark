#!/usr/bin/env python3
"""Setup: send 4 emails simulating a thread about homepage redesign.

Since we send from one account, we create separate emails that form a
logical thread. The last email contains the decision: "Let's go with Option B."
"""

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
        "subject": "Homepage Redesign - Decision Needed",
        "body": (
            "From: Alice Johnson\n\n"
            "Hi team,\n\n"
            "We need to decide on the homepage redesign direction by end of week. "
            "I have prepared two options:\n\n"
            "Option A: Minimalist design with a large hero image and single call-to-action button.\n"
            "Option B: Dynamic layout with featured content grid and multiple entry points.\n\n"
            "Please review the mockups and share your thoughts.\n\nAlice"
        ),
    },
    {
        "subject": "Re: Homepage Redesign - Decision Needed (Priya)",
        "body": (
            "From: Priya Patel\n\n"
            "I reviewed both mockups. I prefer Option B because it gives us more flexibility "
            "to highlight different content. Our analytics show users engage more when there "
            "are multiple content pathways.\n\nPriya"
        ),
    },
    {
        "subject": "Re: Homepage Redesign - Decision Needed (David)",
        "body": (
            "From: David Lee\n\n"
            "From an engineering perspective, both are feasible within the current sprint. "
            "Option A would take about 3 days, Option B closer to 5. "
            "I am slightly leaning toward Option B for the long-term content strategy benefits.\n\nDavid"
        ),
    },
    {
        "subject": "Re: Homepage Redesign - Decision Needed (Marcus - FINAL)",
        "body": (
            "From: Marcus Webb\n\n"
            "Thanks for the thoughtful input. After reviewing the mockups and considering "
            "the team's feedback, I have made a decision.\n\n"
            "Let's go with Option B. The dynamic layout aligns better with our Q2 content "
            "strategy, and David's estimate of 5 days is acceptable given the added flexibility.\n\n"
            "Marcus Webb\nHead of Product Design"
        ),
    },
]

send_emails(test_email, label_name, EMAILS)
ids = poll_for_messages(label_name, len(EMAILS))
label_messages(ids, label_name)
write_manifest(workspace, label_name, ids, test_email)
