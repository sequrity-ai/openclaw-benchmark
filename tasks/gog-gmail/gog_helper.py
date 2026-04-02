"""Shared helper for gog-gmail task setup/teardown scripts.

Provides the gog() CLI wrapper, label management, email sending,
delivery polling, and manifest writing.
"""

import json
import os
import subprocess
import sys
import time
import uuid


def get_workspace():
    return sys.argv[1] if len(sys.argv) > 1 else "/workspace"


def get_test_email():
    email = os.environ.get("GOG_TEST_EMAIL")
    if not email:
        print("ERROR: GOG_TEST_EMAIL environment variable is required", file=sys.stderr)
        sys.exit(1)
    return email


def gog(*args: str, parse_json: bool = False):
    """Run a gog command, optionally parsing JSON output."""
    cmd = ["gog"] + list(args)
    if parse_json:
        cmd.append("--json")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"gog command failed: {' '.join(cmd)}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    if parse_json:
        return json.loads(result.stdout)
    return result.stdout.strip()


def _extract_thread_ids(search_result) -> list[str]:
    """Extract thread/message IDs from gog gmail search JSON output.

    gog returns {"threads": [...]} where each thread has an "id" field.
    """
    threads = []
    if isinstance(search_result, dict):
        threads = search_result.get("threads", [])
    elif isinstance(search_result, list):
        threads = search_result
    return [str(t["id"]) for t in threads if t.get("id")]


def create_label():
    """Create a unique label for this test run. Returns label name."""
    run_id = uuid.uuid4().hex[:8]
    label_name = f"openclawbench-{run_id}"
    print(f"Creating label: {label_name}")
    gog("gmail", "labels", "create", label_name)
    return label_name


def send_emails(test_email: str, label_name: str, emails: list[dict]) -> None:
    """Send a list of emails to the test address.

    Each email dict must have 'subject' and 'body' keys.
    The label_name is prefixed to subjects automatically.
    """
    print(f"Sending {len(emails)} test emails to {test_email} ...")
    for email in emails:
        gog("gmail", "send",
            "--to", test_email,
            "--subject", f"{label_name} | {email['subject']}",
            "--body", email["body"])
        time.sleep(0.5)


def poll_for_messages(label_name: str, expected_count: int, max_wait: int = 120) -> list[str]:
    """Poll Gmail until expected_count messages arrive. Returns message IDs."""
    print("Waiting for emails to arrive ...")
    poll_interval = 5
    elapsed = 0
    message_ids = []

    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        results = gog("gmail", "search", f'subject:"{label_name}"', "--max", "50", parse_json=True)
        message_ids = _extract_thread_ids(results)
        if len(message_ids) >= expected_count:
            break
        print(f"  ... found {len(message_ids)}/{expected_count} messages after {elapsed}s")

    if len(message_ids) < expected_count:
        print(f"WARNING: only {len(message_ids)}/{expected_count} emails arrived after {max_wait}s",
              file=sys.stderr)

    print(f"Collected {len(message_ids)} message IDs")
    return message_ids


def label_messages(message_ids: list[str], label_name: str) -> None:
    """Apply the test label to all messages."""
    if message_ids:
        gog("gmail", "batch", "modify", *message_ids, "--add", label_name)
        print(f"Applied label '{label_name}' to {len(message_ids)} messages")


def mark_read_unread(message_ids: list[str], emails: list[dict], label_name: str) -> None:
    """Mark messages read/unread based on 'unread' key in email dicts.

    Marks all as read first, then marks specific ones back as unread.
    """
    if not message_ids:
        return

    gog("gmail", "batch", "modify", *message_ids, "--remove", "UNREAD")
    print("Marked all messages as read")

    unread_subjects = [e["subject"] for e in emails if e.get("unread")]
    unread_ids = []
    for subject in unread_subjects:
        results = gog("gmail", "search", f'subject:"{subject}"', "--max", "1", parse_json=True)
        ids = _extract_thread_ids(results)
        if ids:
            unread_ids.append(ids[0])

    if unread_ids:
        gog("gmail", "batch", "modify", *unread_ids, "--add", "UNREAD")
        print(f"Marked {len(unread_ids)} messages as unread")


def write_manifest(workspace: str, label_name: str, message_ids: list[str],
                   test_email: str, **extra) -> None:
    """Write manifest and label file to workspace."""
    manifest = {
        "label": label_name,
        "message_ids": message_ids,
        "test_email": test_email,
        **extra,
    }
    manifest_path = os.path.join(workspace, ".manifest.json")
    label_path = os.path.join(workspace, "test_label.txt")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    with open(label_path, "w") as f:
        f.write(label_name)
    # Make files readable by all users (setup runs as root, agent may run as another user)
    os.chmod(manifest_path, 0o644)
    os.chmod(label_path, 0o644)
    print(f"Workspace ready: {workspace}")
