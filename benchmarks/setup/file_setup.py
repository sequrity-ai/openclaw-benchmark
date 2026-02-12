"""Setup utilities for file manipulation benchmark scenario."""

import json
import os
import shutil
from pathlib import Path


class FileSetup:
    """Handles setup and cleanup for file manipulation benchmarks."""

    def __init__(self, workspace_dir: str = "/tmp/openclaw_benchmark"):
        """Initialize file setup.

        Args:
            workspace_dir: Directory for test files
        """
        self.workspace_dir = Path(workspace_dir)
        self.data_json_path = self.workspace_dir / "data.json"
        self.notes_txt_path = self.workspace_dir / "notes.txt"
        self.reports_dir = self.workspace_dir / "reports"

    def create_workspace(self) -> dict[str, str]:
        """Create test workspace with seed files.

        Returns:
            Dict with paths to created files
        """
        # Create directories
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Create data.json with sample user records
        sample_data = {
            "users": [
                {"name": "Alice Johnson", "email": "alice@example.com", "role": "Engineer"},
                {"name": "Bob Smith", "email": "bob@example.com", "role": "Designer"},
                {"name": "Carol White", "email": "carol@example.com", "role": "Manager"},
            ]
        }

        with open(self.data_json_path, "w") as f:
            json.dump(sample_data, f, indent=2)

        # Create notes.txt with meeting notes
        notes_content = """Project Kickoff Meeting Notes
Date: 2026-02-11

Attendees: Alice, Bob, Carol

Discussion Points:
- Project timeline and milestones
- Resource allocation
- Communication protocols

Action Items:
- Alice: Set up development environment by Friday
- Bob: Create initial design mockups for review
- Carol: Schedule follow-up meeting for next week
- Everyone: Review project requirements document

Next Steps:
The team will reconvene next Tuesday to review progress and address
any blockers that have come up.
"""

        with open(self.notes_txt_path, "w") as f:
            f.write(notes_content)

        return {
            "workspace_dir": str(self.workspace_dir),
            "data_json": str(self.data_json_path),
            "notes_txt": str(self.notes_txt_path),
            "reports_dir": str(self.reports_dir),
            "expected_users": sample_data["users"],
        }

    def cleanup_workspace(self) -> bool:
        """Remove test workspace.

        Returns:
            True if cleanup succeeded
        """
        try:
            if self.workspace_dir.exists():
                shutil.rmtree(self.workspace_dir)
            return True
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False

    def verify_workspace_access(self) -> bool:
        """Verify we can read/write to workspace.

        Returns:
            True if workspace is accessible
        """
        try:
            # Try to create a test file
            test_file = self.workspace_dir / ".test"
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
