"""Web research benchmark scenario."""

import logging

from benchmarks.base import (
    BenchmarkTask,
    CheckStatus,
    HealthCheckResult,
    ScenarioBase,
    SetupResult,
)
from benchmarks.setup.web_setup import WebSetup
from benchmarks.validators.web_validator import WebValidator

logger = logging.getLogger(__name__)


class WebScenario(ScenarioBase):
    """Benchmark scenario for web research capabilities."""

    def __init__(self):
        """Initialize web research scenario."""
        super().__init__(
            name="Web Research",
            description="Tests agent's ability to browse web pages, extract information, and cite sources",
            required_skills=["web_browsing", "information_extraction", "research"],
        )

        self.web_setup = WebSetup()
        self.validator = WebValidator()

        # Define tasks
        self._define_tasks()

    def _define_tasks(self) -> None:
        """Define the 3 web research tasks."""

        # Task 1: Factual Extraction
        self.add_task(
            BenchmarkTask(
                name="Factual Extraction",
                prompt=(
                    f"Go to {self.web_setup.wikipedia_url} and tell me when Python was created "
                    "and who created it. Give me specific dates and names."
                ),
                expected_output_description="Founding date and creator information for Python",
                validation_fn=self.validator.validate_factual_extraction,
                timeout=40.0,
                metadata={"difficulty": "low", "category": "factual_extraction"},
            )
        )

        # Task 2: Repository Analysis
        self.add_task(
            BenchmarkTask(
                name="Repository Analysis",
                prompt=(
                    f"Analyze the GitHub repository at {self.web_setup.github_repo_url}. "
                    "Tell me what the repository is about and what its main purpose is."
                ),
                expected_output_description="Description of repository purpose and content",
                validation_fn=self.validator.validate_repo_analysis,
                timeout=50.0,
                metadata={"difficulty": "medium", "category": "code_analysis"},
            )
        )

        # Task 3: Multi-Source Research
        self.add_task(
            BenchmarkTask(
                name="Multi-Source Research",
                prompt=(
                    f"Research '{self.web_setup.search_topic}' and give me 3 key capabilities "
                    "or features. For each capability, provide a source URL where you found the information."
                ),
                expected_output_description="3 capabilities with source URLs",
                validation_fn=self.validator.validate_multi_source_research,
                timeout=60.0,
                metadata={"difficulty": "medium", "category": "research_synthesis"},
            )
        )

    def pre_check(self) -> list[HealthCheckResult]:
        """Run pre-flight health checks.

        Returns:
            List of health check results
        """
        checks = []

        # Check 1: Internet connectivity and URL accessibility
        accessible, message = self.web_setup.verify_urls_accessible()
        if accessible:
            checks.append(
                HealthCheckResult(
                    check_name="URL Accessibility",
                    status=CheckStatus.PASS,
                    message=message,
                    details={
                        "wikipedia_url": self.web_setup.wikipedia_url,
                        "github_url": self.web_setup.github_repo_url,
                    },
                )
            )
        else:
            checks.append(
                HealthCheckResult(
                    check_name="URL Accessibility",
                    status=CheckStatus.FAIL,
                    message=message,
                    details={
                        "wikipedia_url": self.web_setup.wikipedia_url,
                        "github_url": self.web_setup.github_repo_url,
                    },
                )
            )

        # Check 2: Bot web browsing capability (placeholder)
        checks.append(
            HealthCheckResult(
                check_name="Web Browsing Skill",
                status=CheckStatus.SKIP,
                message="Web browsing skill check requires bot query (not implemented)",
                details={"required_skills": self.required_skills},
            )
        )

        return checks

    def setup(self) -> SetupResult:
        """Set up the web research scenario.

        Returns:
            Setup result with test URLs
        """
        try:
            logger.info("Preparing test URLs and topics...")
            setup_data = self.web_setup.prepare_test_urls()

            logger.info(f"Test URLs prepared:")
            logger.info(f"  - Wikipedia: {setup_data['wikipedia_url']}")
            logger.info(f"  - GitHub: {setup_data['github_repo_url']}")
            logger.info(f"  - Research topic: {setup_data['search_topic']}")

            return SetupResult(
                status=CheckStatus.PASS,
                message="Web research URLs prepared successfully",
                setup_data=setup_data,
            )

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return SetupResult(
                status=CheckStatus.FAIL,
                message=f"Failed to prepare URLs: {str(e)}",
                error=str(e),
            )

    def cleanup(self) -> bool:
        """Clean up the web research scenario.

        Returns:
            True (no cleanup needed for web research)
        """
        logger.info("No cleanup needed for web research scenario")
        return True
