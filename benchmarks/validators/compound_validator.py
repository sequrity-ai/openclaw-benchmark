"""Validation utilities for Compound benchmark tasks."""

import logging
from typing import Any

from benchmarks.base import TaskResult

logger = logging.getLogger(__name__)


class CompoundValidator:
    """Validates compound multi-skill task results."""

    @staticmethod
    def validate_weather_then_web(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 1: Weather + Web — check weather, then search for travel tips."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must mention weather data
            weather_keywords = ["temperature", "weather", "degrees", "celsius", "fahrenheit", "°", "forecast", "humid", "wind"]
            has_weather = any(kw in response_lower for kw in weather_keywords)

            # Must mention web search / travel content
            travel_keywords = ["tip", "tips", "pack", "packing", "visit", "travel", "bring", "recommend", "clothing", "sunscreen", "umbrella", "jacket"]
            has_travel = any(kw in response_lower for kw in travel_keywords)

            has_content = len(response) > 80

            validation_details["has_weather_data"] = has_weather
            validation_details["has_travel_content"] = has_travel
            validation_details["has_content"] = has_content

            if has_weather and has_travel and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must include both weather data and travel/packing recommendations"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Weather + Web Research",
            prompt="Check weather and search for travel tips",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_web_then_summarize(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 2: Web + Summarize — search for an article then summarize it."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must contain summary-like content
            summary_keywords = ["summary", "summarize", "article", "discusses", "covers", "explains", "describes", "key point", "main", "according to"]
            has_summary = any(kw in response_lower for kw in summary_keywords)

            # Must be substantive
            has_content = len(response) > 100

            # Must not be an error
            error_patterns = ["could not", "unable to", "failed to", "no results", "not found"]
            is_error = any(pat in response_lower for pat in error_patterns)

            validation_details["has_summary_content"] = has_summary
            validation_details["has_content"] = has_content
            validation_details["is_error"] = is_error

            if has_summary and has_content and not is_error:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must include a substantive summary of a found article"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Web Search + Summarize",
            prompt="Search for article then summarize it",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_github_then_summarize(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 3: GitHub + Summarize — read file from repo and summarize its purpose."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must mention GitHub/file content
            github_keywords = ["file", "function", "code", "module", "class", "import", "async", "javascript", "js", "readme", "repository"]
            has_github = any(kw in response_lower for kw in github_keywords)

            # Must contain summary language
            summary_keywords = ["purpose", "provides", "implements", "defines", "contains", "used for", "responsible", "handles", "summary", "overview"]
            has_summary = any(kw in response_lower for kw in summary_keywords)

            has_content = len(response) > 80

            validation_details["has_github_content"] = has_github
            validation_details["has_summary_language"] = has_summary
            validation_details["has_content"] = has_content

            if has_github and has_summary and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must read a repo file and summarize its purpose"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="GitHub + Summarize",
            prompt="Read repo file and summarize its purpose",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_weather_then_github(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 4: Weather + GitHub — check weather and create an issue reporting it."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must mention weather data in response
            weather_keywords = ["temperature", "weather", "degrees", "°", "celsius", "fahrenheit", "forecast", "conditions"]
            has_weather = any(kw in response_lower for kw in weather_keywords)

            # Must confirm issue was created
            issue_keywords = ["issue", "created", "opened", "#", "filed", "submitted"]
            has_issue = any(kw in response_lower for kw in issue_keywords)

            validation_details["has_weather_data"] = has_weather
            validation_details["has_issue_confirmation"] = has_issue

            if has_weather and has_issue:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must include weather data and confirm GitHub issue creation"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Weather + GitHub Issue",
            prompt="Check weather then file a GitHub issue with conditions",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_web_then_github(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 5: Web + GitHub — search for Python async info then create an issue."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must show web search results about the topic
            search_keywords = ["async", "python", "found", "result", "article", "source", "according", "search"]
            has_search = any(kw in response_lower for kw in search_keywords)

            # Must confirm issue created
            issue_keywords = ["issue", "created", "opened", "#", "filed"]
            has_issue = any(kw in response_lower for kw in issue_keywords)

            validation_details["has_search_results"] = has_search
            validation_details["has_issue_confirmation"] = has_issue

            if has_search and has_issue:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must show web research results and confirm GitHub issue was created"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Web Research + GitHub Issue",
            prompt="Research topic on web then file GitHub issue summarizing findings",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_weather_web_compare(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 6: Weather + Web — compare weather across cities with web-enhanced context."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must mention multiple cities/locations
            city_keywords = ["london", "tokyo", "paris", "berlin", "city", "cities", "location"]
            has_cities = any(kw in response_lower for kw in city_keywords)

            # Must have weather data
            weather_keywords = ["temperature", "weather", "degrees", "°", "warmer", "colder", "humidity", "forecast"]
            has_weather = any(kw in response_lower for kw in weather_keywords)

            # Must have comparison language
            compare_keywords = ["compared", "versus", "vs", "warmer", "colder", "hotter", "cooler", "difference", "while", "whereas"]
            has_comparison = any(kw in response_lower for kw in compare_keywords)

            has_content = len(response) > 80

            validation_details["has_cities"] = has_cities
            validation_details["has_weather_data"] = has_weather
            validation_details["has_comparison"] = has_comparison
            validation_details["has_content"] = has_content

            if has_cities and has_weather and has_comparison and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must compare weather across multiple cities with contextual information"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Multi-City Weather + Context",
            prompt="Compare weather across cities with web-enhanced context",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_github_web_research(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 7: GitHub + Web — get repo info then research the technology online."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must mention repo/GitHub content
            repo_keywords = ["repository", "repo", "commit", "star", "fork", "branch", "javascript", "js", "node"]
            has_repo = any(kw in response_lower for kw in repo_keywords)

            # Must have web research content
            web_keywords = ["search", "found", "article", "according", "source", "web", "online", "result"]
            has_web = any(kw in response_lower for kw in web_keywords)

            has_content = len(response) > 100

            validation_details["has_repo_info"] = has_repo
            validation_details["has_web_research"] = has_web
            validation_details["has_content"] = has_content

            if has_repo and has_web and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must include repo information and web research about the technology"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="GitHub Repo + Web Research",
            prompt="Get repo info then research the technology stack online",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_three_skill_chain(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 8: Web + Weather + GitHub — 3-skill chain."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must have web search content
            web_keywords = ["search", "found", "result", "article", "source", "top", "popular"]
            has_web = any(kw in response_lower for kw in web_keywords)

            # Must have weather content
            weather_keywords = ["temperature", "weather", "degrees", "°", "forecast", "conditions"]
            has_weather = any(kw in response_lower for kw in weather_keywords)

            # Must confirm GitHub issue created
            issue_keywords = ["issue", "created", "opened", "#", "filed"]
            has_issue = any(kw in response_lower for kw in issue_keywords)

            has_content = len(response) > 100

            validation_details["has_web_results"] = has_web
            validation_details["has_weather_data"] = has_weather
            validation_details["has_github_issue"] = has_issue
            validation_details["has_content"] = has_content

            if has_web and has_weather and has_issue and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must demonstrate all three skills: web search, weather data, and GitHub issue creation"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Web + Weather + GitHub Chain",
            prompt="3-skill chain: search web, check weather, file GitHub issue",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )

    @staticmethod
    def validate_summarize_then_github(response: str, setup_data: dict[str, Any]) -> TaskResult:
        """Validate Task 9: Web + Summarize + GitHub — research, summarize, and file findings."""
        success = False
        accuracy_score = 0.0
        validation_details = {}
        error_message = None

        try:
            response_lower = response.lower()

            # Must have summary content
            summary_keywords = ["summary", "summarize", "key point", "main", "discusses", "covers", "article", "source"]
            has_summary = any(kw in response_lower for kw in summary_keywords)

            # Must confirm GitHub issue created
            issue_keywords = ["issue", "created", "opened", "#", "filed", "submitted"]
            has_issue = any(kw in response_lower for kw in issue_keywords)

            has_content = len(response) > 100

            validation_details["has_summary"] = has_summary
            validation_details["has_github_issue"] = has_issue
            validation_details["has_content"] = has_content

            if has_summary and has_issue and has_content:
                success = True
                accuracy_score = 100.0
            else:
                error_message = "Response must include a summary of found content and confirm GitHub issue was filed"

        except Exception as e:
            error_message = f"Validation error: {str(e)}"

        return TaskResult(
            task_name="Research + Summarize + GitHub",
            prompt="Search web, summarize findings, file GitHub issue with summary",
            success=success,
            latency=0.0,
            accuracy_score=accuracy_score,
            response_text=response,
            validation_details=validation_details,
            error_message=error_message,
        )
