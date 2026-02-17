"""Benchmark scenarios for OpenClaw capabilities."""

from .compound_scenario import CompoundScenario
from .file_scenario import FileScenario
from .github_scenario import GitHubScenario
from .gmail_scenario import GmailScenario
from .summarize_scenario import SummarizeScenario
from .weather_scenario import WeatherScenario
from .web_scenario import WebScenario

__all__ = [
    "CompoundScenario",
    "FileScenario",
    "GmailScenario",
    "GitHubScenario",
    "SummarizeScenario",
    "WeatherScenario",
    "WebScenario",
]

# Map of scenario name -> class for CLI lookup
SCENARIO_MAP = {
    "compound": CompoundScenario,
    "file": FileScenario,
    "gmail": GmailScenario,
    "web": WebScenario,
    "weather": WeatherScenario,
    "summarize": SummarizeScenario,
    "github": GitHubScenario,
}
