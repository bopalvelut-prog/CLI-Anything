"""LangChain adapter for CLI-Anything harnesses.

Usage:
    from cli_anything.adapters.langchain import CLITool

    tool = CLITool("gimp")
    result = tool.run("convert input.png output.jpg --quality 90")
"""

try:
    from langchain.tools import BaseTool
    from langchain.callbacks.manager import CallbackManagerForToolRun
    from pydantic import Field

    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    BaseTool = object

import subprocess
import json
from typing import Optional, Type


if HAS_LANGCHAIN:

    class CLITool(BaseTool):
        """A LangChain tool that wraps a CLI-Anything harness."""

        name: str = Field(description="Harness name (e.g. 'gimp', 'blender')")
        description: str = Field(
            default="Execute a CLI-Anything command. Input should be a command string.",
            description="Tool description",
        )
        json_output: bool = Field(default=True, description="Return JSON output")

        def _run(
            self,
            command: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            """Execute a CLI-Anything command."""
            cmd = f"cli-anything-{self.name}"
            args = command.split()

            if self.json_output:
                args = ["--json"] + args

            try:
                result = subprocess.run(
                    [cmd] + args,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if self.json_output:
                    try:
                        return json.dumps(json.loads(result.stdout), indent=2)
                    except json.JSONDecodeError:
                        return result.stdout
                return result.stdout
            except FileNotFoundError:
                return f"Error: cli-anything-{self.name} not found. Install with: cli-anything install {self.name}"
            except subprocess.TimeoutExpired:
                return "Error: Command timed out"


def create_langchain_tools(apps: list) -> list:
    """Create LangChain tools for multiple harnesses."""
    if not HAS_LANGCHAIN:
        raise ImportError("Install langchain: pip install langchain")

    tools = []
    for app in apps:
        tool = CLITool(name=app)
        tools.append(tool)
    return tools
