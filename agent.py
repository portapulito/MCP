# ./adk_agent_samples/mcp_image_agent/agent.py
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Optional: You can set environment variables for MCP-Images if needed
# For MCP-Images, typically no API key is required since it processes local/URL images
# But you might want to set the path to your MCP-Images installation
google_api_key = os.environ.get("GOOGLE_API_KEY")

mcp_path = r"C:\Users\simon\mcp-images"

root_agent = Agent(
    model='gemini-2.0-flash',
    name='img_agent',
    instruction='Help the user process, fetch, and analyze images from URLs or local file paths using MCP Images tools. You can handle multiple images at once and return them as base64-encoded data with MIME types.',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='uv',
                args=[
                    '--directory', 
                    mcp_path,
                    'run',
                    'mcp_image.py'
                ],
            ),
            
            
        )
    ],
)