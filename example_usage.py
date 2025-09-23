#!/usr/bin/env python3
"""
Example usage of Dremio MCP Server and AI Agent

This script demonstrates how to use the Dremio client and AI agent
programmatically for data analysis and exploration.
"""

import asyncio
import os
from dotenv import load_dotenv

from dremio_client import DremioClient
from ai_agent import DremioAIAgent

# Load environment variables
load_dotenv()

async def main():
    """Main example function"""
    
    # Configuration
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true',
        'cert_path': os.getenv('DREMIO_CERT_PATH'),
        'flight_port': int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))),
        'default_source': os.getenv('DREMIO_DEFAULT_SOURCE'),
        'default_schema': os.getenv('DREMIO_DEFAULT_SCHEMA')
    }
    
    print("🚀 Dremio MCP Server and AI Agent Example")
    print("=" * 50)
    
    # Initialize Dremio client
    use_ssl = config['use_ssl']
    verify_ssl = config['verify_ssl']
    host = config['host']
    port = config['port']
    scheme = 'https' if use_ssl else 'http'
    
    print(f"📡 Connecting to Dremio at {scheme}://{host}:{port} (verify_ssl={'on' if verify_ssl else 'off'})...")
    if config.get('cert_path'):
        print(f"Using CA bundle: {config['cert_path']}")
    if config.get('default_source') or config.get('default_schema'):
        print(f"Default scope: source={config.get('default_source')}, schema={config.get('default_schema')}")
    
    client = DremioClient(config)
    
    if not client.authenticate():
        print("❌ Failed to authenticate with Dremio")
        return
    
    print("✅ Successfully connected to Dremio!")
    
    # Initialize AI agent
    agent = DremioAIAgent(client)
    
    # Set Anthropic API key if available
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        agent.set_openai_key(openai_key)
        print("🤖 AI Agent initialized with OpenAI support")
    else:
        print("🤖 AI Agent initialized (basic mode)")
    
    print("\n" + "=" * 50)
    
    # Example 1: List available tables
    print("\n📋 Example 1: Listing available tables")
    print("-" * 30)
    
    try:
        tables = client.list_tables()
        print(f"Found {len(tables)} tables:")
        for schema, table in tables[:10]:  # Show first 10
            print(f"  - {schema}.{table}")
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more tables")
    except Exception as e:
        print(f"❌ Error listing tables: {e}")
    
    # Example 2: Get table schema
    print("\n📊 Example 2: Getting table schema")
    print("-" * 30)
    
    if tables:
        sample_table = f"{tables[0][0]}.{tables[0][1]}"
        print(f"Getting schema for: {sample_table}")
        
        try:
            schema_df = client.get_table_schema(sample_table)
            print("Schema:")
            print(schema_df.to_string(index=False))
        except Exception as e:
            print(f"❌ Error getting schema: {e}")
    
    # Example 3: Natural language query
    print("\n🗣️  Example 3: Natural language query")
    print("-" * 30)
    
    if tables:
        sample_table = f"{tables[0][0]}.{tables[0][1]}"
        query = f"Show me the first 5 rows from {sample_table}"
        print(f"Query: '{query}'")
        
        try:
            result = await agent.process_query(query)
            if result.get('success'):
                print("✅ Query successful!")
                if 'data' in result and result['data']:
                    print(f"Returned {len(result['data'])} rows")
                    # Show first few columns of first row
                    if result['data']:
                        first_row = result['data'][0]
                        print("Sample data:")
                        for key, value in list(first_row.items())[:3]:
                            print(f"  {key}: {value}")
                        if len(first_row) > 3:
                            print(f"  ... and {len(first_row) - 3} more columns")
            else:
                print(f"❌ Query failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    # Example 4: Search for tables
    print("\n🔍 Example 4: Searching for tables")
    print("-" * 30)
    
    search_term = "customer"  # Common table name
    print(f"Searching for tables containing '{search_term}'")
    
    try:
        result = await agent.process_query(f"Find tables with {search_term} in the name")
        if result.get('success') and 'tables' in result:
            tables_found = result['tables']
            print(f"Found {len(tables_found)} tables:")
            for table in tables_found[:5]:
                print(f"  - {table}")
        else:
            print("No tables found or search failed")
    except Exception as e:
        print(f"❌ Error searching tables: {e}")
    
    # Example 5: Get metadata
    print("\n📚 Example 5: Getting table metadata")
    print("-" * 30)
    
    if tables:
        sample_table = f"{tables[0][0]}.{tables[0][1]}"
        print(f"Getting metadata for: {sample_table}")
        
        try:
            metadata = client.get_dataset_metadata(sample_table)
            if metadata:
                print("Metadata retrieved successfully!")
                if metadata.get('wiki_description'):
                    print(f"Description: {metadata['wiki_description'][:100]}...")
                if metadata.get('sample_data'):
                    print(f"Sample data available: {len(metadata['sample_data'])} rows")
            else:
                print("No metadata available")
        except Exception as e:
            print(f"❌ Error getting metadata: {e}")
    
    # Example 6: Direct SQL query
    print("\n💾 Example 6: Direct SQL query")
    print("-" * 30)
    
    if tables:
        sample_table = f"{tables[0][0]}.{tables[0][1]}"
        sql_query = f"SELECT COUNT(*) as total_rows FROM {sample_table}"
        print(f"Executing: {sql_query}")
        
        try:
            result_df = client.execute_query(sql_query)
            print("Query result:")
            print(result_df.to_string(index=False))
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Example completed!")
    print("\nNext steps:")
    print("1. Try the interactive CLI: python cli.py interactive")
    print("2. Start the MCP server: python cli.py start-server")
    print("3. Configure Claude Desktop with the provided config")
    print("4. Ask natural language questions about your data!")

if __name__ == "__main__":
    asyncio.run(main())
