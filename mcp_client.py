import asyncio
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
import json

# Configuration
SERVER_SCRIPT = str(Path(__file__).parent / "mcp_server.py")

async def call_tool(tool_name: str, arguments: dict) -> dict:
    """Start the server, call one MCP tool, and parse its JSON result."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            return json.loads(result.content[0].text)


async def list_tools() -> list[str]:
    """Ask the server which tools it exposes."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return [tool.name for tool in result.tools]
