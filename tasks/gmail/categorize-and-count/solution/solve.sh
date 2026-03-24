#!/bin/bash
# Reference solution for categorize-and-count.

mkdir -p /workspace/.logs/agent

python3 - <<'PYEOF'
billing_keywords = ["invoice", "billing", "payment", "remit", "subscription", "amount due", "retainer fee"]
meeting_keywords = ["meeting", "town hall", "1:1", "invite", "join", "zoom", "reschedule"]
project_keywords = ["project", "sprint", "update", "progress", "milestone", "launch", "refactor", "redesign", "campaign", "migration", "kickoff"]

def categorize_email(subject, body):
    text = (subject + " " + body).lower()
    billing_score = sum(1 for kw in billing_keywords if kw in text)
    meeting_score = sum(1 for kw in meeting_keywords if kw in text)
    project_score = sum(1 for kw in project_keywords if kw in text)

    if billing_score >= meeting_score and billing_score >= project_score and billing_score > 0:
        return "Billing"
    elif meeting_score >= project_score and meeting_score > 0:
        return "Meetings"
    else:
        return "Project Updates"

with open("/workspace/inbox.txt", "r") as f:
    content = f.read()

emails = content.split("\n---\n")

counts = {"Billing": 0, "Meetings": 0, "Project Updates": 0}

for email in emails:
    email = email.strip()
    if not email:
        continue
    subject = ""
    body_lines = []
    in_body = False
    for line in email.splitlines():
        if line.startswith("Subject:"):
            subject = line[len("Subject:"):].strip()
        elif line.strip() == "" and not in_body and subject:
            in_body = True
        elif in_body:
            body_lines.append(line)
    body = " ".join(body_lines)
    cat = categorize_email(subject, body)
    counts[cat] += 1

response = f"Billing: {counts['Billing']}\nMeetings: {counts['Meetings']}\nProject Updates: {counts['Project Updates']}"

with open("/workspace/.logs/agent/response.txt", "w") as f:
    f.write(response)

print(response)
PYEOF
