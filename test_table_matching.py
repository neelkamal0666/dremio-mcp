#!/usr/bin/env python3
"""
Test script for table name matching fixes

This script tests the improved table name matching logic.
"""

import asyncio
import os
from dotenv import load_dotenv
from ai_agent import DremioAIAgent
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def test_table_matching():
    """Test the table name matching functionality"""
    print("🧪 Testing Table Name Matching")
    print("=" * 40)
    
    # Create Dremio client
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', 'admin'),
        'password': os.getenv('DREMIO_PASSWORD', 'admin'),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true',
        'cert_path': os.getenv('DREMIO_CERT_PATH'),
        'flight_port': int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))),
        'default_source': os.getenv('DREMIO_DEFAULT_SOURCE'),
        'default_schema': os.getenv('DREMIO_DEFAULT_SCHEMA'),
    }
    
    try:
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Failed to authenticate with Dremio")
            return
        
        print("✅ Connected to Dremio successfully")
        
        # Get available tables
        tables = client.list_tables()
        print(f"📋 Found {len(tables)} tables:")
        for schema, table in tables[:10]:  # Show first 10
            print(f"  - {schema}.{table}")
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more")
        
        # Create AI agent
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            print("⚠️  No Anthropic API key found - testing heuristic only")
            agent = DremioAIAgent(client)
        else:
            agent = DremioAIAgent(client, anthropic_api_key=anthropic_key)
        
        # Test queries
        test_queries = [
            "how many accounts are there",
            "show me all customers",
            "count the users",
            "how many orders do we have",
            "show me product information"
        ]
        
        print("\n🔍 Testing Query Processing:")
        print("-" * 30)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            
            # Test intent analysis
            intent = agent._analyze_query_intent(query)
            print(f"Intent: {intent['intent']}")
            
            # Test heuristic SQL generation
            heuristic_sql = agent._generate_sql_heuristic(query, intent)
            if heuristic_sql:
                print(f"✅ Heuristic SQL: {heuristic_sql}")
            else:
                print("❌ No heuristic SQL generated")
            
            # Test AI SQL generation if available
            if anthropic_key:
                try:
                    ai_sql = asyncio.run(agent._generate_sql_with_ai(query, intent))
                    if ai_sql:
                        print(f"✅ AI SQL: {ai_sql}")
                    else:
                        print("❌ No AI SQL generated")
                except Exception as e:
                    print(f"❌ AI SQL error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_full_query_processing():
    """Test full query processing with table matching"""
    print("\n🧪 Testing Full Query Processing")
    print("=" * 40)
    
    # Create Dremio client
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', 'admin'),
        'password': os.getenv('DREMIO_PASSWORD', 'admin'),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true',
        'cert_path': os.getenv('DREMIO_CERT_PATH'),
        'flight_port': int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010'))),
        'default_source': os.getenv('DREMIO_DEFAULT_SOURCE'),
        'default_schema': os.getenv('DREMIO_DEFAULT_SCHEMA'),
    }
    
    try:
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Failed to authenticate with Dremio")
            return
        
        # Create AI agent
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not anthropic_key:
            print("⚠️  No Anthropic API key found - skipping full processing test")
            return
        
        agent = DremioAIAgent(client, anthropic_api_key=anthropic_key)
        
        # Test the specific query that was failing
        test_query = "how many accounts are there"
        print(f"Testing: '{test_query}'")
        
        result = await agent.process_query(test_query)
        
        if result.get('success'):
            print("✅ Query processed successfully!")
            if 'data' in result:
                print(f"📊 Result: {result['data']}")
            if 'sql_query' in result:
                print(f"🔍 SQL: {result['sql_query']}")
        else:
            print(f"❌ Query failed: {result.get('error')}")
            if 'suggestion' in result:
                print(f"💡 Suggestion: {result['suggestion']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main test function"""
    print("🚀 Table Name Matching Test Suite")
    print("=" * 50)
    
    # Test table matching
    test_table_matching()
    
    # Test full query processing
    await test_full_query_processing()
    
    print("\n" + "=" * 50)
    print("🎉 Table matching tests completed!")
    print("\nThe fixes should resolve the 'object accounts not found' error.")
    print("Now queries like 'how many accounts are there' should find the correct table!")

if __name__ == "__main__":
    asyncio.run(main())
