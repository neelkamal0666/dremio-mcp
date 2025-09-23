#!/usr/bin/env python3
"""
Command Line Interface for Dremio MCP Server and AI Agent

This CLI provides an interactive interface for:
- Testing the MCP server
- Running the AI agent
- Managing Dremio connections
- Exploring data with natural language
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

import click
from dotenv import load_dotenv

from dremio_client import DremioClient
from ai_agent import DremioAIAgent
from dremio_mcp_server_json import DremioMCPServerJSON

# Load environment variables
load_dotenv()

@click.group()
def cli():
    """Dremio MCP Server and AI Agent CLI"""
    pass

@cli.command()
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio port')
@click.option('--username', default=os.getenv('DREMIO_USERNAME', ''), help='Dremio username')
@click.option('--password', default=os.getenv('DREMIO_PASSWORD', ''), help='Dremio password')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--flight-port', default=int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))), help='Dremio Flight SQL port')
@click.option('--default-source', default=os.getenv('DREMIO_DEFAULT_SOURCE'), help='Default source to scope listings')
@click.option('--default-schema', default=os.getenv('DREMIO_DEFAULT_SCHEMA'), help='Default schema to scope listings')
def test_connection(host, port, username, password, ssl, verify, cert_path, flight_port, default_source, default_schema):
    """Test connection to Dremio"""
    config = {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'use_ssl': ssl,
        'verify_ssl': verify,
        'cert_path': cert_path,
        'flight_port': flight_port,
        'default_source': default_source,
        'default_schema': default_schema,
    }
    
    click.echo(f"Testing connection to {host}:{port} (ssl={'on' if ssl else 'off'}, verify={'on' if verify else 'off'}, flight_port={flight_port})...")
    
    try:
        client = DremioClient(config)
        if client.authenticate():
            click.echo("✅ Successfully connected to Dremio!")
            
            # Test a simple query
            try:
                tables = client.list_tables()
                click.echo(f"Found {len(tables)} tables")
                if tables:
                    click.echo("Sample tables:")
                    for schema, table in tables[:5]:
                        click.echo(f"  - {schema}.{table}")
            except Exception as e:
                click.echo(f"⚠️  Connection successful but query failed: {e}")
        else:
            click.echo("❌ Failed to authenticate with Dremio")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Connection failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--openai-key', help='OpenAI API key for enhanced AI features (defaults to OPENAI_API_KEY env var)')
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio REST port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL for REST')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--flight-port', default=int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))), help='Dremio Flight SQL port')
@click.option('--default-source', default=os.getenv('DREMIO_DEFAULT_SOURCE'), help='Default source to scope listings (defaults to DREMIO_DEFAULT_SOURCE)')
@click.option('--default-schema', default=os.getenv('DREMIO_DEFAULT_SCHEMA'), help='Default schema to scope listings (defaults to DREMIO_DEFAULT_SCHEMA)')
def interactive(openai_key, host, port, ssl, verify, cert_path, flight_port, default_source, default_schema):
    """Start interactive AI agent session"""
    asyncio.run(_interactive_async(openai_key, host, port, ssl, verify, cert_path, flight_port, default_source, default_schema))

async def _interactive_async(openai_key, host, port, ssl, verify, cert_path, flight_port, default_source, default_schema):
    """Async implementation of interactive session"""
    # Prefer explicit flag; fallback to environment variable
    if not openai_key:
        openai_key = os.getenv('OPENAI_API_KEY')
    # If defaults are still None, fall back to env here as well
    default_source = default_source or os.getenv('DREMIO_DEFAULT_SOURCE')
    default_schema = default_schema or os.getenv('DREMIO_DEFAULT_SCHEMA')
    
    config = {
        'host': host,
        'port': port,
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': ssl,
        'verify_ssl': verify,
        'cert_path': cert_path,
        'flight_port': flight_port,
        'default_source': default_source,
        'default_schema': default_schema,
    }
    
    if not config['username'] or not config['password']:
        click.echo("❌ Please set DREMIO_USERNAME and DREMIO_PASSWORD environment variables")
        sys.exit(1)
    
    click.echo(f"Connecting to {('https' if ssl else 'http')}://{host}:{port} (verify={'on' if verify else 'off'}, flight_port={flight_port})...")
    if cert_path:
        click.echo(f"Using CA bundle: {cert_path}")
    if default_source or default_schema:
        click.echo(f"Default scope: source={default_source}, schema={default_schema}")
    if openai_key:
        click.echo("Using OpenAI key from environment/flag")
    
    try:
        # Initialize client and agent
        client = DremioClient(config)
        if not client.authenticate():
            click.echo("❌ Failed to authenticate with Dremio")
            sys.exit(1)
        
        agent = DremioAIAgent(client)
        if openai_key:
            agent.set_openai_key(openai_key)
            click.echo("🤖 AI Agent initialized with OpenAI support")
        else:
            click.echo("🤖 AI Agent initialized (basic mode - set OPENAI_API_KEY in .env or use --openai-key)")
        
        click.echo("✅ Connected to Dremio! Type 'help' for commands or ask questions about your data.")
        click.echo("Type 'exit' to quit.\n")
        
        # Interactive loop
        while True:
            try:
                user_input = click.prompt("Dremio AI", type=str).strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                elif user_input.lower() == 'tables':
                    show_tables(client)
                    continue
                elif user_input.lower().startswith('schema '):
                    table_name = user_input[7:].strip()
                    show_schema(client, table_name)
                    continue
                elif user_input.lower().startswith('sample '):
                    table_name = user_input[7:].strip()
                    show_sample(client, table_name)
                    continue
                
                # Process natural language query (now properly awaited)
                result = await agent.process_query(user_input)
                display_result(result)
                
            except KeyboardInterrupt:
                click.echo("\nGoodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
                
    except Exception as e:
        click.echo(f"❌ Failed to start interactive session: {e}")
        sys.exit(1)

@cli.command()
@click.option('--query', required=True, help='SQL query to execute')
@click.option('--limit', default=100, help='Maximum number of rows to return')
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--flight-port', default=int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))), help='Dremio Flight SQL port')
@click.option('--default-source', default=os.getenv('DREMIO_DEFAULT_SOURCE'), help='Default source to scope listings')
@click.option('--default-schema', default=os.getenv('DREMIO_DEFAULT_SCHEMA'), help='Default schema to scope listings')
def query(query, limit, host, port, ssl, verify, cert_path, flight_port, default_source, default_schema):
    """Execute a SQL query directly"""
    config = {
        'host': host,
        'port': port,
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': ssl,
        'verify_ssl': verify,
        'cert_path': cert_path,
        'flight_port': flight_port,
        'default_source': default_source,
        'default_schema': default_schema,
    }
    
    try:
        client = DremioClient(config)
        if not client.authenticate():
            click.echo("❌ Failed to authenticate with Dremio")
            sys.exit(1)
        
        result_df = client.execute_query(query, limit)
        
        click.echo(f"Query executed successfully. Returned {len(result_df)} rows.")
        click.echo("\nResults:")
        click.echo(result_df.to_string(index=False))
        
    except Exception as e:
        click.echo(f"❌ Query failed: {e}")
        sys.exit(1)

@cli.group()
def mcp_json():
    """Call JSON MCP server tools directly"""
    pass

@mcp_json.command("tables")
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio REST port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL for REST')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--username', default=os.getenv('DREMIO_USERNAME', ''), help='Dremio username')
@click.option('--password', default=os.getenv('DREMIO_PASSWORD', ''), help='Dremio password')
def mcp_json_tables(host, port, ssl, verify, cert_path, username, password):
    """List tables using JSON MCP server"""
    # Propagate connection settings to env for server initialization
    os.environ['DREMIO_HOST'] = str(host)
    os.environ['DREMIO_PORT'] = str(port)
    os.environ['DREMIO_USE_SSL'] = 'true' if ssl else 'false'
    os.environ['DREMIO_VERIFY_SSL'] = 'true' if verify else 'false'
    if cert_path:
        os.environ['DREMIO_CERT_PATH'] = str(cert_path)
    if username:
        os.environ['DREMIO_USERNAME'] = str(username)
    if password:
        os.environ['DREMIO_PASSWORD'] = str(password)

    async def _run():
        server = DremioMCPServerJSON()
        result = await server._list_tables_json({})
        click.echo(json.dumps(result, indent=2, default=str))
    try:
        asyncio.run(_run())
    except Exception as e:
        click.echo(f"❌ MCP JSON tables failed: {e}")
        sys.exit(1)

@mcp_json.command("ask")
@click.option('--question', '-q', required=True, prompt=True, help='Natural language question')
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio REST port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL for REST')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--username', default=os.getenv('DREMIO_USERNAME', ''), help='Dremio username')
@click.option('--password', default=os.getenv('DREMIO_PASSWORD', ''), help='Dremio password')
def mcp_json_ask(question: str, host, port, ssl, verify, cert_path, username, password):
    """Ask a natural language question via JSON MCP server"""
    # Propagate connection settings to env for server initialization
    os.environ['DREMIO_HOST'] = str(host)
    os.environ['DREMIO_PORT'] = str(port)
    os.environ['DREMIO_USE_SSL'] = 'true' if ssl else 'false'
    os.environ['DREMIO_VERIFY_SSL'] = 'true' if verify else 'false'
    if cert_path:
        os.environ['DREMIO_CERT_PATH'] = str(cert_path)
    if username:
        os.environ['DREMIO_USERNAME'] = str(username)
    if password:
        os.environ['DREMIO_PASSWORD'] = str(password)

    async def _run():
        server = DremioMCPServerJSON()
        result = await server._process_natural_language_query_json({
            "question": question
        })
        click.echo(json.dumps(result, indent=2, default=str))
    try:
        asyncio.run(_run())
    except Exception as e:
        click.echo(f"❌ MCP JSON ask failed: {e}")
        sys.exit(1)

@mcp_json.command("sql")
@click.option('--query', '-Q', required=True, help='SQL query to execute')
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio REST port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL for REST')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--username', default=os.getenv('DREMIO_USERNAME', ''), help='Dremio username')
@click.option('--password', default=os.getenv('DREMIO_PASSWORD', ''), help='Dremio password')
def mcp_json_sql(query: str, host, port, ssl, verify, cert_path, username, password):
    """Run a SQL query via JSON MCP server"""
    # Propagate connection settings to env for server initialization
    os.environ['DREMIO_HOST'] = str(host)
    os.environ['DREMIO_PORT'] = str(port)
    os.environ['DREMIO_USE_SSL'] = 'true' if ssl else 'false'
    os.environ['DREMIO_VERIFY_SSL'] = 'true' if verify else 'false'
    if cert_path:
        os.environ['DREMIO_CERT_PATH'] = str(cert_path)
    if username:
        os.environ['DREMIO_USERNAME'] = str(username)
    if password:
        os.environ['DREMIO_PASSWORD'] = str(password)

    async def _run():
        server = DremioMCPServerJSON()
        result = await server._query_dremio_json({
            "query": query
        })
        click.echo(json.dumps(result, indent=2, default=str))
    try:
        asyncio.run(_run())
    except Exception as e:
        click.echo(f"❌ MCP JSON sql failed: {e}")
        sys.exit(1)

@mcp_json.command("metadata")
@click.option('--table', '-t', required=True, help='Fully qualified table name')
@click.option('--host', default=os.getenv('DREMIO_HOST', 'localhost'), help='Dremio host')
@click.option('--port', default=int(os.getenv('DREMIO_PORT', '9047')), help='Dremio REST port')
@click.option('--ssl/--no-ssl', default=os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true', help='Use SSL for REST')
@click.option('--verify/--no-verify', default=os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true', help='Verify SSL certificates')
@click.option('--cert-path', default=os.getenv('DREMIO_CERT_PATH'), help='Custom CA bundle path')
@click.option('--username', default=os.getenv('DREMIO_USERNAME', ''), help='Dremio username')
@click.option('--password', default=os.getenv('DREMIO_PASSWORD', ''), help='Dremio password')
def mcp_json_metadata(table: str, host, port, ssl, verify, cert_path, username, password):
    """Get table metadata via JSON MCP server"""
    # Propagate connection settings to env for server initialization
    os.environ['DREMIO_HOST'] = str(host)
    os.environ['DREMIO_PORT'] = str(port)
    os.environ['DREMIO_USE_SSL'] = 'true' if ssl else 'false'
    os.environ['DREMIO_VERIFY_SSL'] = 'true' if verify else 'false'
    if cert_path:
        os.environ['DREMIO_CERT_PATH'] = str(cert_path)
    if username:
        os.environ['DREMIO_USERNAME'] = str(username)
    if password:
        os.environ['DREMIO_PASSWORD'] = str(password)

    async def _run():
        server = DremioMCPServerJSON()
        result = await server._get_table_metadata_json({
            "table": table
        })
        click.echo(json.dumps(result, indent=2, default=str))
    try:
        asyncio.run(_run())
    except Exception as e:
        click.echo(f"❌ MCP JSON metadata failed: {e}")
        sys.exit(1)

@cli.command()
def start_server():
    """Start the MCP server"""
    import subprocess
    import sys
    
    click.echo("Starting Dremio MCP Server...")
    try:
        subprocess.run([sys.executable, "dremio_mcp_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Server failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")

def show_help():
    """Show help information"""
    help_text = """
Available commands:
  help                    - Show this help message
  tables                  - List all available tables
  schema <table_name>     - Show schema for a specific table
  sample <table_name>     - Show sample data from a table
  exit/quit/q             - Exit the session

Natural language queries:
  "Show me all tables in the sales schema"
  "What is the schema of customer_data table?"
  "How many records are in the orders table?"
  "Show me the first 10 rows from products table"
  "What columns are in the users table?"
  "Tell me about the customer_data table"
    """
    click.echo(help_text)

def show_tables(client: DremioClient):
    """Show available tables"""
    try:
        tables = client.list_tables()
        if tables:
            click.echo(f"Found {len(tables)} tables:")
            for schema, table in tables:
                click.echo(f"  - {schema}.{table}")
        else:
            click.echo("No tables found")
    except Exception as e:
        click.echo(f"❌ Error listing tables: {e}")

def show_schema(client: DremioClient, table_name: str):
    """Show schema for a table"""
    try:
        schema_df = client.get_table_schema(table_name)
        click.echo(f"Schema for {table_name}:")
        click.echo(schema_df.to_string(index=False))
    except Exception as e:
        click.echo(f"❌ Error getting schema: {e}")

def show_sample(client: DremioClient, table_name: str):
    """Show sample data from a table"""
    try:
        sample_df = client.get_data_sample(table_name, 10)
        click.echo(f"Sample data from {table_name}:")
        click.echo(sample_df.to_string(index=False))
    except Exception as e:
        click.echo(f"❌ Error getting sample data: {e}")

def display_result(result: Dict[str, Any]):
    """Display query result in a formatted way"""
    if not result.get('success', False):
        click.echo(f"❌ {result.get('error', 'Unknown error')}")
        if 'suggestion' in result:
            click.echo(f"💡 Suggestion: {result['suggestion']}")
        return
    
    # Display different types of results
    if 'data' in result:
        data = result['data']
        if data:
            click.echo(f"✅ Query successful! Found {result.get('row_count', len(data))} rows.")
            
            # Show first few rows
            display_data = data[:10]  # Show first 10 rows
            if display_data:
                # Convert to formatted table
                import pandas as pd
                df = pd.DataFrame(display_data)
                click.echo("\nResults:")
                click.echo(df.to_string(index=False))
                
                if len(data) > 10:
                    click.echo(f"\n... (showing first 10 of {len(data)} rows)")
        else:
            click.echo("✅ Query successful but no data returned.")
    
    elif 'schema' in result:
        schema = result['schema']
        click.echo(f"✅ Schema for {result.get('table', 'table')}:")
        import pandas as pd
        df = pd.DataFrame(schema)
        click.echo(df.to_string(index=False))
    
    elif 'tables' in result:
        tables = result['tables']
        click.echo(f"✅ Found {len(tables)} tables:")
        for table in tables:
            click.echo(f"  - {table}")
    
    elif 'metadata' in result:
        metadata = result['metadata']
        click.echo(f"✅ Metadata for {result.get('table', 'table')}:")
        click.echo(json.dumps(metadata, indent=2, default=str))
    
    else:
        click.echo("✅ Query completed successfully!")

if __name__ == '__main__':
    cli()
