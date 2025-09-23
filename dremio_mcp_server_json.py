#!/usr/bin/env python3
"""
Enhanced Dremio MCP Server with JSON Responses
Returns structured JSON responses similar to Flask API
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
from dremio_client import DremioClient
from ai_agent_bedrock import DremioAIAgentBedrock

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
    verify_ssl: bool = True
    cert_path: Optional[str] = None
    flight_port: Optional[int] = None
    default_source: Optional[str] = None
    default_schema: Optional[str] = None

class DremioMCPServerJSON:
    """Enhanced MCP server with JSON responses"""
    
    def __init__(self):
        self.server = Server("dremio-mcp-server-json")
        self.config = self._load_config()
        self.client = self._create_client()
        self.ai_agent = self._create_ai_agent()
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
            client_secret=os.getenv("DREMIO_CLIENT_SECRET"),
            verify_ssl=os.getenv("DREMIO_VERIFY_SSL", "true").lower() == "true",
            cert_path=os.getenv("DREMIO_CERT_PATH"),
            flight_port=int(os.getenv("DREMIO_FLIGHT_PORT", os.getenv("DREMIO_PORT", "32010"))),
            default_source=os.getenv("DREMIO_DEFAULT_SOURCE"),
            default_schema=os.getenv("DREMIO_DEFAULT_SCHEMA"),
        )
    
    def _create_client(self) -> DremioClient:
        """Create Dremio client"""
        cfg = {
            'host': self.config.host,
            'port': self.config.port,
            'username': self.config.username,
            'password': self.config.password,
            'use_ssl': self.config.use_ssl,
            'verify_ssl': self.config.verify_ssl,
            'cert_path': self.config.cert_path,
            'flight_port': self.config.flight_port,
            'default_source': self.config.default_source,
            'default_schema': self.config.default_schema,
        }
        client = DremioClient(cfg)
        if not client.authenticate():
            logger.error("Failed to authenticate Dremio client for MCP server")
        return client
    
    def _create_ai_agent(self) -> Optional[DremioAIAgentBedrock]:
        """Create AI agent with Bedrock or OpenAI support"""
        # Check for Bedrock configuration first
        bedrock_model_id = os.getenv('BEDROCK_MODEL_ID')
        aws_region = os.getenv('AWS_REGION')
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if bedrock_model_id and aws_region and aws_access_key and aws_secret_key:
            try:
                ai_agent = DremioAIAgentBedrock(
                    self.client, 
                    provider="bedrock", 
                    bedrock_model_id=bedrock_model_id
                )
                logger.info(f"AI agent initialized with Bedrock model: {bedrock_model_id}")
                return ai_agent
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock AI agent: {e}")
        
        # Fallback to OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                ai_agent = DremioAIAgentBedrock(self.client, provider="openai")
                ai_agent.set_openai_key(openai_key)
                logger.info("AI agent initialized with OpenAI")
                return ai_agent
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI AI agent: {e}")
        
        # No AI agent available
        logger.warning("No AI agent available. Using heuristic SQL generation only.")
        return None
    
    def _setup_handlers(self):
        """Setup MCP server handlers"""
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            tools = [
                Tool(
                    name="query_dremio",
                    description="Execute SQL query against Dremio and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of rows to return (default: 1000)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_table_schema",
                    description="Get schema information for a table and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_path": {
                                "type": "string",
                                "description": "Full path to the table (e.g., 'DataMesh.application.accounts')"
                            }
                        },
                        "required": ["table_path"]
                    }
                ),
                Tool(
                    name="list_tables",
                    description="List all available tables and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Filter by source name"
                            },
                            "schema": {
                                "type": "string",
                                "description": "Filter by schema name"
                            }
                        }
                    }
                ),
                Tool(
                    name="search_tables",
                    description="Search for tables by name and return structured JSON response",
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
                    name="get_wiki_description",
                    description="Get wiki description for a table and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_path": {
                                "type": "string",
                                "description": "Full path to the table"
                            }
                        },
                        "required": ["table_path"]
                    }
                ),
                Tool(
                    name="get_wiki_metadata",
                    description="Get comprehensive wiki metadata for a table and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_path": {
                                "type": "string",
                                "description": "Full path to the table"
                            }
                        },
                        "required": ["table_path"]
                    }
                ),
                Tool(
                    name="search_wiki_content",
                    description="Search wiki content across tables and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_term": {
                                "type": "string",
                                "description": "Search term to find in wiki content"
                            }
                        },
                        "required": ["search_term"]
                    }
                ),
                Tool(
                    name="process_natural_language_query",
                    description="Process natural language questions and return structured JSON response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Natural language question about the data"
                            }
                        },
                        "required": ["question"]
                    }
                )
            ]
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls with JSON responses"""
            try:
                if name == "query_dremio":
                    result = await self._query_dremio_json(arguments)
                elif name == "get_table_schema":
                    result = await self._get_table_schema_json(arguments)
                elif name == "list_tables":
                    result = await self._list_tables_json(arguments)
                elif name == "search_tables":
                    result = await self._search_tables_json(arguments)
                elif name == "get_wiki_description":
                    result = await self._get_wiki_description_json(arguments)
                elif name == "get_wiki_metadata":
                    result = await self._get_wiki_metadata_json(arguments)
                elif name == "search_wiki_content":
                    result = await self._search_wiki_content_json(arguments)
                elif name == "process_natural_language_query":
                    result = await self._process_natural_language_query_json(arguments)
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown tool: {name}",
                        "error_code": "UNKNOWN_TOOL"
                    }
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                )
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                error_result = {
                    "success": False,
                    "error": f"Error executing tool {name}: {str(e)}",
                    "error_code": "TOOL_EXECUTION_ERROR"
                }
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(error_result, indent=2))]
                )
    
    async def _query_dremio_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query and return JSON response"""
        query = arguments.get("query", "")
        limit = arguments.get("limit", 1000)
        
        if not query.strip():
            return {
                "success": False,
                "error": "Query cannot be empty",
                "error_code": "EMPTY_QUERY"
            }
        
        try:
            # Add LIMIT if not present and limit is specified
            if limit and "LIMIT" not in query.upper():
                query = f"{query} LIMIT {limit}"

            df = self.client.execute_query(query)
            
            if df is None or df.empty:
                return {
                    "success": True,
                    "query_type": "data_query",
                    "data": {
                        "rows": [],
                        "row_count": 0,
                        "columns": [],
                        "message": "No data found"
                    }
                }
            
            # Convert DataFrame to list of dictionaries
            rows = df.to_dict('records')
            columns = list(df.columns)
            column_types = {col: str(df[col].dtype) for col in columns}
            
            # Check if this is a count query
            is_count_query = any(word in query.upper() for word in ['COUNT(', 'COUNT (*)'])
            
            return {
                "success": True,
                "query_type": "data_query",
                "data": {
                    "rows": rows,
                    "row_count": len(rows),
                    "columns": columns,
                    "column_types": column_types,
                    "is_count_query": is_count_query,
                    "message": f"Found {len(rows)} rows"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing query: {str(e)}",
                "error_code": "QUERY_EXECUTION_ERROR"
            }
    
    async def _get_table_schema_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get table schema and return JSON response"""
        table_path = arguments.get("table_path", "")
        
        if not table_path:
            return {
                "success": False,
                "error": "Table path is required",
                "error_code": "MISSING_TABLE_PATH"
            }
        
        try:
            schema = self.client.get_table_schema(table_path)
            
            if not schema:
                return {
                    "success": False,
                    "error": f"Table '{table_path}' not found or no schema information available",
                    "error_code": "TABLE_NOT_FOUND"
                }
            
            return {
                "success": True,
                "query_type": "metadata_request",
                "data": {
                    "table_name": table_path,
                    "schema": schema,
                    "column_count": len(schema),
                    "message": f"Schema for table '{table_path}'"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting schema: {str(e)}",
                "error_code": "SCHEMA_ERROR"
            }
    
    async def _list_tables_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List tables and return JSON response"""
        source = arguments.get("source")
        schema = arguments.get("schema")
        
        try:
            tables = self.client.list_tables()
            
            # Apply filters if provided
            filtered_tables = tables
            if source:
                filtered_tables = [t for t in tables if source.lower() in t.lower()]
            if schema:
                filtered_tables = [t for t in filtered_tables if schema.lower() in t.lower()]
            
            return {
                "success": True,
                "query_type": "table_exploration",
                "data": {
                    "tables": filtered_tables,
                    "total_count": len(filtered_tables),
                    "all_tables_count": len(tables),
                    "message": f"Found {len(filtered_tables)} tables"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing tables: {str(e)}",
                "error_code": "LIST_TABLES_ERROR"
            }
    
    async def _search_tables_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search tables and return JSON response"""
        search_term = arguments.get("search_term", "")
        
        if not search_term:
            return {
                "success": False,
                "error": "Search term is required",
                "error_code": "MISSING_SEARCH_TERM"
            }
        
        try:
            results = self.client.search_datasets(search_term)
            
            return {
                "success": True,
                "query_type": "table_exploration",
                "data": {
                    "tables": results,
                    "total_count": len(results),
                    "search_term": search_term,
                    "message": f"Found {len(results)} tables matching '{search_term}'"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching tables: {str(e)}",
                "error_code": "SEARCH_ERROR"
            }
    
    async def _get_wiki_description_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get wiki description and return JSON response"""
        table_path = arguments.get("table_path", "")
        
        if not table_path:
            return {
                "success": False,
                "error": "Table path is required",
                "error_code": "MISSING_TABLE_PATH"
            }
        
        try:
            wiki_description = self.client.get_wiki_description(table_path)
            
            if not wiki_description:
                return {
                    "success": True,
                    "query_type": "metadata_request",
                    "data": {
                        "table_name": table_path,
                        "wiki_description": None,
                        "message": f"No wiki description found for table '{table_path}'"
                    }
                }
            
            return {
                "success": True,
                "query_type": "metadata_request",
                "data": {
                    "table_name": table_path,
                    "wiki_description": wiki_description,
                    "message": f"Wiki description for table '{table_path}'"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting wiki description: {str(e)}",
                "error_code": "WIKI_ERROR"
            }
    
    async def _get_wiki_metadata_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get wiki metadata and return JSON response"""
        table_path = arguments.get("table_path", "")
        
        if not table_path:
            return {
                "success": False,
                "error": "Table path is required",
                "error_code": "MISSING_TABLE_PATH"
            }
        
        try:
            wiki_metadata = self.client.get_wiki_metadata(table_path)
            
            return {
                "success": True,
                "query_type": "metadata_request",
                "data": {
                    "table_name": table_path,
                    "wiki_metadata": wiki_metadata,
                    "message": f"Wiki metadata for table '{table_path}'"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting wiki metadata: {str(e)}",
                "error_code": "WIKI_METADATA_ERROR"
            }
    
    async def _search_wiki_content_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search wiki content and return JSON response"""
        search_term = arguments.get("search_term", "")
        
        if not search_term:
            return {
                "success": False,
                "error": "Search term is required",
                "error_code": "MISSING_SEARCH_TERM"
            }
        
        try:
            results = self.client.search_wiki_content(search_term)
            
            return {
                "success": True,
                "query_type": "metadata_request",
                "data": {
                    "search_term": search_term,
                    "results": results,
                    "total_count": len(results),
                    "message": f"Found {len(results)} wiki entries matching '{search_term}'"
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching wiki content: {str(e)}",
                "error_code": "WIKI_SEARCH_ERROR"
            }
    
    async def _process_natural_language_query_json(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Process natural language query and return JSON response"""
        question = arguments.get("question", "")
        
        if not question:
            return {
                "success": False,
                "error": "Question is required",
                "error_code": "MISSING_QUESTION"
            }
        
        try:
            if self.ai_agent:
                # Use AI agent for natural language processing
                response = self.ai_agent.process_query(question)
                return {
                    "success": True,
                    "query_type": "natural_language_query",
                    "data": {
                        "question": question,
                        "response": response,
                        "message": "Natural language query processed with AI"
                    }
                }
            else:
                # Fallback to basic processing
                return {
                    "success": False,
                    "error": "AI agent not available. Please provide OpenAI API key.",
                    "error_code": "AI_AGENT_NOT_AVAILABLE"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing natural language query: {str(e)}",
                "error_code": "NATURAL_LANGUAGE_ERROR"
            }
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dremio-mcp-server-json",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

# Create global instance
dremio_mcp_server = DremioMCPServerJSON()

async def main():
    """Main function to run the MCP server"""
    await dremio_mcp_server.run()

if __name__ == "__main__":
    asyncio.run(main())
