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
def test_connection(host, port, username, password, ssl):
    """Test connection to Dremio"""
    config = {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'use_ssl': ssl
    }
    
    click.echo(f"Testing connection to {host}:{port}...")
    
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
@click.option('--openai-key', help='OpenAI API key for enhanced AI features')
def interactive(openai_key):
    """Start interactive AI agent session"""
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true'
    }
    
    if not config['username'] or not config['password']:
        click.echo("❌ Please set DREMIO_USERNAME and DREMIO_PASSWORD environment variables")
        sys.exit(1)
    
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
            click.echo("🤖 AI Agent initialized (basic mode - set OpenAI key for enhanced features)")
        
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
                
                # Process natural language query
                result = asyncio.run(agent.process_query(user_input))
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
def query(query, limit):
    """Execute a SQL query directly"""
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true'
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
