"""Validation utilities for web research tasks."""

import re
from typing import Any

from benchmarks.base import TaskResult


class WebValidator:
    """Validates web research task results."""

    @staticmethod
    def validate_factual_extraction(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 1: Factual extraction from Wikipedia.

        Expected: Founding date and headquarters location of Python
        """
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Check for founding/creation year (Python was created in 1991)
            year_patterns = [
                r"199[01]",  # 1990 or 1991
                r"early 1990s",
                r"late 1980s",
            ]

            found_year = False
            for pattern in year_patterns:
                if re.search(pattern, response_lower):
                    found_year = True
                    accuracy_score += 50.0
                    break

            validation_details["found_year"] = found_year

            # Check for location/organization info
            # Python was created by Guido van Rossum, often mentions Netherlands or CWI
            location_keywords = [
                "netherlands",
                "dutch",
                "guido",
                "van rossum",
                "cwi",
                "centrum wiskunde",
            ]

            found_location = False
            for keyword in location_keywords:
                if keyword in response_lower:
                    found_location = True
                    accuracy_score += 50.0
                    break

            validation_details["found_location"] = found_location

            # Success if we found both pieces of information
            if found_year and found_location:
                success = True
                accuracy_score = 100.0
            elif not found_year and not found_location:
                error_message = "Response does not contain founding date or location information"
            elif not found_year:
                error_message = "Response missing founding/creation date"
            else:
                error_message = "Response missing creator/location information"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Factual Extraction",
            prompt=f"Go to {setup_data.get('wikipedia_url', 'Wikipedia')} and tell me about Python's creation",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_repo_analysis(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 2: GitHub repository analysis.

        Expected: Primary language, stars, and main purpose
        """
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Check for repository name/identification
            repo_name = setup_data.get("github_expected", {}).get("repo", "")
            if "openclaw" in response_lower or "usecases" in response_lower:
                accuracy_score += 30.0
                validation_details["identified_repo"] = True
            else:
                validation_details["identified_repo"] = False

            # Check for purpose/description
            purpose_keywords = [
                "use case",
                "example",
                "showcase",
                "collection",
                "awesome",
                "list",
            ]

            found_purpose = False
            for keyword in purpose_keywords:
                if keyword in response_lower:
                    found_purpose = True
                    accuracy_score += 40.0
                    break

            validation_details["found_purpose"] = found_purpose

            # Check for any metadata (stars, language, etc.)
            metadata_indicators = [
                "star",
                "⭐",
                "language",
                "markdown",
                "repository",
                "github",
            ]

            found_metadata = False
            for indicator in metadata_indicators:
                if indicator in response_lower:
                    found_metadata = True
                    accuracy_score += 30.0
                    break

            validation_details["found_metadata"] = found_metadata

            if accuracy_score >= 70.0:
                success = True
                if accuracy_score == 100.0:
                    accuracy_score = 100.0

            if not success:
                missing = []
                if not validation_details["identified_repo"]:
                    missing.append("repository identification")
                if not found_purpose:
                    missing.append("purpose description")
                if not found_metadata:
                    missing.append("repository metadata")
                error_message = f"Missing: {', '.join(missing)}"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Repository Analysis",
            prompt=f"Analyze {setup_data.get('github_repo_url', 'the repository')} and describe it",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_multi_source_research(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 3: Multi-source research with citations.

        Expected: 3 capabilities with source URLs
        """
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            # Count distinct capabilities mentioned
            capability_keywords = [
                "telegram",
                "automation",
                "task",
                "agent",
                "skill",
                "integration",
                "api",
                "workflow",
                "memory",
                "persistent",
                "browser",
                "email",
                "calendar",
                "file",
            ]

            mentioned_capabilities = []
            for keyword in capability_keywords:
                if keyword in response.lower():
                    mentioned_capabilities.append(keyword)

            # Count unique capabilities (at least 3)
            unique_capabilities = len(set(mentioned_capabilities))
            validation_details["unique_capabilities"] = unique_capabilities

            if unique_capabilities >= 3:
                accuracy_score += 40.0
            elif unique_capabilities >= 2:
                accuracy_score += 25.0
            elif unique_capabilities >= 1:
                accuracy_score += 10.0

            # Count URLs in response
            url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
            urls = re.findall(url_pattern, response)
            validation_details["url_count"] = len(urls)
            validation_details["urls"] = urls

            if len(urls) >= 3:
                accuracy_score += 60.0
            elif len(urls) >= 2:
                accuracy_score += 40.0
            elif len(urls) >= 1:
                accuracy_score += 20.0

            # Success if we have 3+ capabilities and 3+ URLs
            if unique_capabilities >= 3 and len(urls) >= 3:
                success = True
                accuracy_score = 100.0
            else:
                missing_parts = []
                if unique_capabilities < 3:
                    missing_parts.append(f"only {unique_capabilities} capabilities (need 3)")
                if len(urls) < 3:
                    missing_parts.append(f"only {len(urls)} sources (need 3)")
                error_message = "Incomplete research: " + ", ".join(missing_parts)

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Multi-Source Research",
            prompt=f"Research '{setup_data.get('search_topic', 'the topic')}' and provide 3 capabilities with sources",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )
