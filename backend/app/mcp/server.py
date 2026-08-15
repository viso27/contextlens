from fastmcp import FastMCP
from app.mcp.tools import fetch_table_context, check_query_safety

mcp = FastMCP("ContextLens-MCP-Server")

@mcp.tool()
async def get_table_context(database: str, table_name: str) -> str:
    """Fetches real-time schema definitions, trust scores, and active/deprecated column rules."""
    return await fetch_table_context(database, table_name)

@mcp.tool()
async def validate_query_safety(query: str, database: str, table_name: str) -> str:
    """Scans SQL/NoSQL query text for usage of deprecated schema fields."""
    return await check_query_safety(query, database, table_name)

if __name__ == "__main__":
    mcp.run()