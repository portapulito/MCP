import os
import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Dict
import openai
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


server_params = StdioServerParameters(
    command="python",
    args=["server.py"],  
    env=None,
)


@dataclass
class Chat:
    messages: list[Dict[str, Any]] = field(default_factory=list)
    system_prompt: str = (
        "You are a Postgres SQL assistant operating in read-only mode. "
        "Only SELECT queries are allowed: you MUST NEVER execute any statements that modify the database (e.g., INSERT, UPDATE, DELETE, CREATE, DROP). "
        "Use the 'query_data' tool strictly for fetching data without side effects."
    )

    async def process_query(self, session: ClientSession, query: str) -> None:
        # Retrieve available tools from the MCP server
        tools_response = await session.list_tools()
        tools = tools_response.tools

       
        functions = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
            for tool in tools
        ]

        
        self.messages.append({"role": "user", "content": query})

        
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
            functions=functions,
            function_call="auto",
        )
        message = completion.choices[0].message

        
        if message.get("function_call"):
            fn_name = message["function_call"]["name"]
            fn_args = json.loads(message["function_call"]["arguments"])

            
            tool_result = await session.call_tool(fn_name, fn_args)
            tool_output = getattr(tool_result.content[0], "text", str(tool_result))

            
            self.messages.append({"role": "assistant", "content": message.to_dict()})
            self.messages.append({
                "role": "function",
                "name": fn_name,
                "content": tool_output,
            })

            
            final_completion = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
            )
            final_message = final_completion.choices[0].message["content"]
            print(final_message)
            self.messages.append({"role": "assistant", "content": final_message})
        else:
            
            content = message.get("content", "")
            print(content)
            self.messages.append({"role": "assistant", "content": content})

    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nSQL> ").strip()
            if not query:
                continue
            await self.process_query(session, query)

    async def run(self):
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await self.chat_loop(session)

if __name__ == "__main__":
    asyncio.run(Chat().run())
