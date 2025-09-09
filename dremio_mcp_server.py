#!/usr/bin/env python3
"""
Dremio MCP Server

This server provides MCP tools for interacting with Dremio, including:
- Querying data from Dremio tables
- Accessing metadata and table schemas
- Reading wiki descriptions for better context
- Natural language query processing
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urljoin

import pandas as pd
import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DremioConfig(BaseModel):
    """Configuration for Dremio connection"""
    host: str
    port: int = 9047
    username: str
    password: str
    use_ssl: bool = True
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

class DremioMCP:
    """Main MCP server class for Dremio integration"""
    
    def __init__(self):
        self.server = Server("dremio-mcp-server")
        self.config = self._load_config()
        self.engine = None
        self.session = None
        self._setup_handlers()
        
    def _load_config(self) -> DremioConfig:
        """Load configuration from environment variables"""
        return DremioConfig(
            host=os.getenv("DREMIO_HOST", "localhost"),
            port=int(os.getenv("DREMIO_PORT", "9047")),
            username=os.getenv("DREMIO_USERNAME", ""),
            password=os.getenv("DREMIO_PASSWORD", ""),
            use_ssl=os.getenv("DREMIO_USE_SSL", "true").lower() == "true",
            client_id=os.getenv("DREMIO_CLIENT_ID"),
            client_secret=os.getenv("DREMIO_CLIENT_SECRET")
        )
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="query_dremio",
                        description="Execute SQL queries against Dremio data sources",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "SQL query to execute"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of rows to return (default: 1000)",
                                    "default": 1000
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="get_table_schema",
                        description="Get schema information for a specific table",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_path": {
                                    "type": "string",
                                    "description": "Full path to the table (e.g., 'source.schema.table')"
                                }
                            },
                            "required": ["table_path"]
                        }
                    ),
                    Tool(
                        name="list_tables",
                        description="List all available tables in Dremio",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                    "description": "Optional source name to filter tables"
                                },
                                "schema": {
                                    "type": "string",
                                    "description": "Optional schema name to filter tables"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_table_metadata",
                        description="Get comprehensive metadata for a table including wiki descriptions",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_path": {
                                    "type": "string",
                                    "description": "Full path to the table (e.g., 'source.schema.table')"
                                }
                            },
                            "required": ["table_path"]
                        }
                    ),
                    Tool(
                        name="search_tables",
                        description="Search for tables by name or description",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "search_term": {
                                    "type": "string",
                                    "description": "Search term to find tables"
                                }
                            },
                            "required": ["search_term"]
                        }
                    ),
                    Tool(
                        name="get_data_sample",
                        description="Get a sample of data from a table for exploration",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_path": {
                                    "type": "string",
                                    "description": "Full path to the table"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of rows to return (default: 10)",
                                    "default": 10
                                }
                            },
                            "required": ["table_path"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "query_dremio":
                    return await self._query_dremio(arguments)
                elif name == "get_table_schema":
                    return await self._get_table_schema(arguments)
                elif name == "list_tables":
                    return await self._list_tables(arguments)
                elif name == "get_table_metadata":
                    return await self._get_table_metadata(arguments)
                elif name == "search_tables":
                    return await self._search_tables(arguments)
                elif name == "get_data_sample":
                    return await self._get_data_sample(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def _get_connection(self):
        """Get or create database connection"""
        if self.engine is None:
            protocol = "dremio+flight" if self.config.use_ssl else "dremio+flight"
            connection_string = f"{protocol}://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}"
            self.engine = create_engine(connection_string)
        return self.engine
    
    async def _query_dremio(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute SQL query against Dremio"""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 1000)
        
        if not query.strip():
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Query cannot be empty")]
            )
        
        try:
            engine = await self._get_connection()
            
            # Add LIMIT if not present and limit is specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                
                # Convert to DataFrame for better formatting
                df = pd.DataFrame(rows, columns=columns)
                
                result_text = f"Query executed successfully. Returned {len(df)} rows.\n\n"
                result_text += df.to_string(index=False, max_rows=100)
                
                if len(df) >= 100:
                    result_text += f"\n\n... (showing first 100 rows of {len(df)} total)"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
        except SQLAlchemyError as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"SQL Error: {str(e)}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing query: {str(e)}")]
            )
    
    async def _get_table_schema(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get schema information for a table"""
        table_path = arguments.get("table_path", "")
        
        try:
            engine = await self._get_connection()
            
            # Query to get table schema
            schema_query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = '{table_path.split('.')[-1]}'
            ORDER BY ordinal_position
            """
            
            with engine.connect() as conn:
                result = conn.execute(text(schema_query))
                columns = result.keys()
                rows = result.fetchall()
                
                if not rows:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Table '{table_path}' not found or no schema information available")]
                    )
                
                df = pd.DataFrame(rows, columns=columns)
                result_text = f"Schema for table '{table_path}':\n\n"
                result_text += df.to_string(index=False)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting schema: {str(e)}")]
            )
    
    async def _list_tables(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List all available tables"""
        source = arguments.get("source")
        schema = arguments.get("schema")
        
        try:
            engine = await self._get_connection()
            
            # Build query based on filters
            query = "SELECT table_schema, table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_type = 'BASE TABLE'"
            params = []
            
            if source:
                query += " AND table_schema LIKE ?"
                params.append(f"{source}%")
            
            if schema:
                query += " AND table_schema = ?"
                params.append(schema)
            
            query += " ORDER BY table_schema, table_name"
            
            with engine.connect() as conn:
                result = conn.execute(text(query), params)
                rows = result.fetchall()
                
                if not rows:
                    return CallToolResult(
                        content=[TextContent(type="text", text="No tables found")]
                    )
                
                result_text = f"Found {len(rows)} tables:\n\n"
                for schema_name, table_name in rows:
                    result_text += f"- {schema_name}.{table_name}\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing tables: {str(e)}")]
            )
    
    async def _get_table_metadata(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive metadata including wiki descriptions"""
        table_path = arguments.get("table_path", "")
        
        try:
            # Get basic schema information
            schema_result = await self._get_table_schema({"table_path": table_path})
            schema_text = schema_result.content[0].text if schema_result.content else "No schema information available"
            
            # Get sample data
            sample_result = await self._get_data_sample({"table_path": table_path, "limit": 5})
            sample_text = sample_result.content[0].text if sample_result.content else "No sample data available"
            
            # Try to get wiki description (this would require Dremio API access)
            wiki_text = await self._get_wiki_description(table_path)
            
            result_text = f"=== METADATA FOR TABLE: {table_path} ===\n\n"
            result_text += f"SCHEMA:\n{schema_text}\n\n"
            
            if wiki_text:
                result_text += f"DESCRIPTION:\n{wiki_text}\n\n"
            
            result_text += f"SAMPLE DATA:\n{sample_text}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting metadata: {str(e)}")]
            )
    
    async def _get_wiki_description(self, table_path: str) -> str:
        """Get wiki description for a table (requires Dremio API)"""
        try:
            # This would require implementing Dremio REST API calls
            # For now, return a placeholder
            return "Wiki description not available (requires Dremio API integration)"
        except Exception:
            return "Wiki description not available"
    
    async def _search_tables(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Search for tables by name or description"""
        search_term = arguments.get("search_term", "").lower()
        
        try:
            engine = await self._get_connection()
            
            # Search in table names
            query = """
            SELECT table_schema, table_name 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE LOWER(table_name) LIKE ? OR LOWER(table_schema) LIKE ?
            ORDER BY table_schema, table_name
            """
            
            search_pattern = f"%{search_term}%"
            
            with engine.connect() as conn:
                result = conn.execute(text(query), [search_pattern, search_pattern])
                rows = result.fetchall()
                
                if not rows:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"No tables found matching '{search_term}'")]
                    )
                
                result_text = f"Found {len(rows)} tables matching '{search_term}':\n\n"
                for schema_name, table_name in rows:
                    result_text += f"- {schema_name}.{table_name}\n"
                
                return CallToolResult(
                    content=[TextContent(type="text", text=result_text)]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error searching tables: {str(e)}")]
            )
    
    async def _get_data_sample(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get sample data from a table"""
        table_path = arguments.get("table_path", "")
        limit = arguments.get("limit", 10)
        
        try:
            query = f"SELECT * FROM {table_path} LIMIT {limit}"
            return await self._query_dremio({"query": query, "limit": limit})
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error getting sample data: {str(e)}")]
            )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dremio-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = DremioMCP()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
