import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    Text,
    Image,
    EmbeddedResourceReference,
    Resource,
    ReadResourceRequest,
    ReadResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
)

from app.db.models import ResearchTaskORM, SessionLocal, init_db
from app.llm.ollama_client import OllamaClient

# Initialize database and Ollama client
init_db()
ollama_client = OllamaClient()

# Create MCP server
server = Server("mcpagent-research")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools for research tasks."""
    tools = [
        Tool(
            name="create_research_task",
            description="Create a new research task with a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research query to investigate"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_research_tasks",
            description="List all research tasks",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="update_research_task",
            description="Update the status or result of a research task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status for the task"
                    },
                    "result": {
                        "type": "string",
                        "description": "New result for the task"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="analyze_content",
            description="Analyze content using Llama 3.2",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Content to analyze"
                    }
                },
                "required": ["content"]
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for research operations."""
    try:
        if name == "create_research_task":
            return await create_research_task(arguments)
        elif name == "list_research_tasks":
            return await list_research_tasks()
        elif name == "update_research_task":
            return await update_research_task(arguments)
        elif name == "analyze_content":
            return await analyze_content(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def create_research_task(arguments: Dict[str, Any]) -> CallToolResult:
    """Create a new research task."""
    query = arguments.get("query")
    if not query:
        return CallToolResult(
            content=[TextContent(type="text", text="Error: query is required")]
        )
    
    db = SessionLocal()
    try:
        task = ResearchTaskORM(
            query=query,
            status="pending",
            result=None
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Generate LLM response in background
        asyncio.create_task(generate_llm_response(task.id, query))
        
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"Research task created with ID {task.id}. Status: {task.status}"
            )]
        )
    finally:
        db.close()

async def list_research_tasks() -> CallToolResult:
    """List all research tasks."""
    db = SessionLocal()
    try:
        tasks = db.query(ResearchTaskORM).all()
        if not tasks:
            return CallToolResult(
                content=[TextContent(type="text", text="No research tasks found.")]
            )
        
        task_list = []
        for task in tasks:
            task_list.append(f"ID: {task.id}, Query: {task.query}, Status: {task.status}")
        
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text="Research Tasks:\n" + "\n".join(task_list)
            )]
        )
    finally:
        db.close()

async def update_research_task(arguments: Dict[str, Any]) -> CallToolResult:
    """Update a research task."""
    task_id = arguments.get("task_id")
    status = arguments.get("status")
    result = arguments.get("result")
    
    if not task_id:
        return CallToolResult(
            content=[TextContent(type="text", text="Error: task_id is required")]
        )
    
    db = SessionLocal()
    try:
        task = db.query(ResearchTaskORM).filter(ResearchTaskORM.id == task_id).first()
        if not task:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Task {task_id} not found")]
            )
        
        if status:
            task.status = status
        if result:
            task.result = result
        
        db.commit()
        
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"Task {task_id} updated successfully. Status: {task.status}"
            )]
        )
    finally:
        db.close()

async def analyze_content(arguments: Dict[str, Any]) -> CallToolResult:
    """Analyze content using Llama 3.2."""
    content = arguments.get("content")
    if not content:
        return CallToolResult(
            content=[TextContent(type="text", text="Error: content is required")]
        )
    
    prompt = f"Analyze and summarize the following content for accuracy, relevance, and key points.\n\nContent:\n{content}"
    analysis = ollama_client.generate(prompt, model="llama3.2")
    
    return CallToolResult(
        content=[TextContent(
            type="text", 
            text=analysis or "LLM did not return a result."
        )]
    )

async def generate_llm_response(task_id: int, query: str):
    """Generate LLM response for a research task in background."""
    db = SessionLocal()
    try:
        task = db.query(ResearchTaskORM).filter(ResearchTaskORM.id == task_id).first()
        if not task:
            return
        
        prompt = f"Generate a robust web scraping strategy for the following research query: '{query}'. Include anti-detection techniques."
        result = ollama_client.generate(prompt, model="codellama")
        
        task.result = result or "LLM did not return a result."
        task.status = "completed"
        db.commit()
    finally:
        db.close()

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcpagent-research",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 