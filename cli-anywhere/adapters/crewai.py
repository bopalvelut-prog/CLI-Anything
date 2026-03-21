"""CrewAI adapter for CLI-Anything harnesses.

Usage:
    from cli_anything.adapters.crewai import CLITool

    tool = CLITool("gimp")
    agent = Agent(tools=[tool], ...)
"""

try:
    from crewai.tools import BaseTool

    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False
    BaseTool = object

import subprocess
import json
from typing import Optional


if HAS_CREWAI:

    class CLITool(BaseTool):
        """A CrewAI tool that wraps a CLI-Anything harness."""

        name: str
        description: str = "Execute a CLI-Anything command"

        def __init__(self, app_name: str, **kwargs):
            self.name = f"cli-anything-{app_name}"
            self.app_name = app_name
            self.description = (
                f"Execute {app_name} commands via CLI-Anything. "
                f"Input should be a command string like 'convert input.png output.jpg'."
            )
            super().__init__(**kwargs)

        def _run(self, command: str) -> str:
            """Execute a CLI-Anything command."""
            cmd = f"cli-anything-{self.app_name}"
            args = ["--json"] + command.split()

            try:
                result = subprocess.run(
                    [cmd] + args,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                try:
                    return json.dumps(json.loads(result.stdout), indent=2)
                except json.JSONDecodeError:
                    return result.stdout
            except FileNotFoundError:
                return f"Error: {cmd} not found. Install with: cli-anything install {self.app_name}"
            except subprocess.TimeoutExpired:
                return "Error: Command timed out"


def create_crewai_tools(apps: list) -> list:
    """Create CrewAI tools for multiple harnesses."""
    if not HAS_CREWAI:
        raise ImportError("Install crewai: pip install crewai")

    return [CLITool(app) for app in apps]
