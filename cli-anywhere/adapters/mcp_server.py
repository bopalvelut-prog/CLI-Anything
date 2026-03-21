"""MCP (Model Context Protocol) server adapter for CLI-Anything.

Provides an MCP-compatible server that exposes CLI-Anything harnesses
as tools for any MCP-compatible AI client (Claude Desktop, etc.).

Usage:
    python -m cli_anything.adapters.mcp_server --apps gimp,blender,inkscape
"""

import json
import subprocess
import sys
import asyncio
from typing import Any


try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def create_server(apps: list[str]) -> Any:
    """Create an MCP server exposing CLI-Anything harnesses."""
    if not HAS_MCP:
        raise ImportError("Install mcp: pip install mcp")

    server = Server("cli-anything")

    @server.list_tools()
    async def list_tools():
        tools = []
        for app in apps:
            tools.append(
                Tool(
                    name=f"cli-anything-{app}",
                    description=f"Execute {app} commands via CLI-Anything harness",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": f"The {app} command to execute",
                            }
                        },
                        "required": ["command"],
                    },
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        app = name.replace("cli-anything-", "")
        command = arguments.get("command", "")

        cmd = f"cli-anything-{app}"
        args = ["--json"] + command.split()

        try:
            result = subprocess.run(
                [cmd] + args,
                capture_output=True,
                text=True,
                timeout=120,
            )

            try:
                output = json.dumps(json.loads(result.stdout), indent=2)
            except json.JSONDecodeError:
                output = result.stdout

            return [TextContent(type="text", text=output)]
        except FileNotFoundError:
            return [
                TextContent(
                    type="text",
                    text=f"Error: {cmd} not found. Install with: cli-anything install {app}",
                )
            ]
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="Error: Command timed out")]

    return server


def main():
    """Run the MCP server."""
    if not HAS_MCP:
        print("Install mcp: pip install mcp")
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser(description="CLI-Anything MCP Server")
    parser.add_argument(
        "--apps",
        default="gimp,blender,inkscape",
        help="Comma-separated list of apps to expose",
    )
    args = parser.parse_args()

    apps = [a.strip() for a in args.apps.split(",")]
    server = create_server(apps)

    print(f"Starting MCP server with apps: {', '.join(apps)}")
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
