"""Secret leak detection and redaction for benchmark outputs.

Scans outbound content (setup writes, agent responses, GitHub issue bodies)
for accidentally leaked API keys, tokens, and environment variable dumps.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Each pattern: (name, compiled regex)
_SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    # OpenAI API keys
    ("openai_api_key", re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}")),
    # OpenRouter keys
    ("openrouter_key", re.compile(r"sk-or-v1-[a-f0-9]{40,}")),
    # GitHub PATs (classic)
    ("github_pat_classic", re.compile(r"ghp_[A-Za-z0-9]{36,}")),
    # GitHub PATs (fine-grained)
    ("github_pat_fine_grained", re.compile(r"github_pat_[A-Za-z0-9_]{22,}")),
    # GitHub OAuth / user / server / refresh tokens
    ("github_oauth_token", re.compile(r"gh[ours]_[A-Za-z0-9]{36,}")),
    # Tavily API keys
    ("tavily_key", re.compile(r"tvly-[A-Za-z0-9]{20,}")),
    # xAI keys
    ("xai_key", re.compile(r"xai-[A-Za-z0-9]{20,}")),
    # Env var assignment patterns (KEY=value)
    (
        "env_var_assignment",
        re.compile(
            r"(?:OPENAI_API_KEY|GITHUB_TOKEN|TAVILY_API_KEY|SEQURITY_API_KEY|OPENROUTER_API_KEY)"
            r"\s*=\s*\S+"
        ),
    ),
    # Bearer tokens
    ("bearer_token", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{20,}")),
    # GitHub-style auth tokens ("token ghp_...")
    ("token_auth", re.compile(r"token\s+[A-Za-z0-9._\-]{20,}")),
    # Hex tokens after '=' (env var dumps like KEY=abc123...)
    ("hex_token_assignment", re.compile(r"=\s*([a-f0-9]{32,64})\b")),
    # Standalone hex tokens on their own line
    ("hex_token_standalone", re.compile(r"^([a-f0-9]{32,64})$", re.MULTILINE)),
]


class SecretScanner:
    """Detects and redacts leaked secrets in text content."""

    @staticmethod
    def scan(text: str) -> list[dict[str, Any]]:
        """Scan text for secret patterns.

        Args:
            text: Text content to scan

        Returns:
            List of dicts with keys: pattern_name, match, position
        """
        if not text:
            return []

        findings: list[dict[str, Any]] = []
        for pattern_name, regex in _SECRET_PATTERNS:
            for m in regex.finditer(text):
                findings.append({
                    "pattern_name": pattern_name,
                    "match": m.group(0),
                    "position": m.start(),
                })
        return findings

    @staticmethod
    def contains_secrets(text: str) -> bool:
        """Check whether text contains any secret patterns.

        Args:
            text: Text content to check

        Returns:
            True if secrets are detected
        """
        if not text:
            return False

        for _, regex in _SECRET_PATTERNS:
            if regex.search(text):
                return True
        return False

    @staticmethod
    def redact(text: str) -> str:
        """Replace detected secrets with [REDACTED].

        Args:
            text: Text content to redact

        Returns:
            Text with secrets replaced by [REDACTED]
        """
        if not text:
            return text

        for _, regex in _SECRET_PATTERNS:
            text = regex.sub("[REDACTED]", text)
        return text
