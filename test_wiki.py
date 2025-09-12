#!/usr/bin/env python3
"""
Test script for Dremio Wiki integration

This script demonstrates the wiki metadata functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from dremio_client import DremioClient
from ai_agent import DremioAIAgent

# Load environment variables
load_dotenv()

async def test_wiki_functionality():
    """Test wiki metadata functionality"""
    print("🧪 Testing Dremio Wiki Integration")
    print("=" * 50)
    
    # Configuration
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true'
    }
    
    if not config['username'] or not config['password']:
        print("❌ Please set DREMIO_USERNAME and DREMIO_PASSWORD environment variables")
        return
    
    try:
        # Initialize client
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Failed to authenticate with Dremio")
            return
        
        print("✅ Successfully connected to Dremio!")
        
        # Initialize AI agent
        agent = DremioAIAgent(client)
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            agent.set_anthropic_key(anthropic_key)
            print("🤖 AI Agent initialized with Claude support")
        else:
            print("🤖 AI Agent initialized (basic mode)")
        
        print("\n" + "=" * 50)
        
        # Test 1: List tables and check for wiki content
        print("\n📋 Test 1: Checking for tables with wiki documentation")
        print("-" * 40)
        
        tables = client.list_tables()
        print(f"Found {len(tables)} tables")
        
        tables_with_wiki = []
        for schema, table in tables[:10]:  # Check first 10 tables
            table_path = f"{schema}.{table}"
            wiki_metadata = client.get_wiki_metadata(table_path)
            if wiki_metadata and wiki_metadata.get('raw_text'):
                tables_with_wiki.append(table_path)
                print(f"✅ {table_path} has wiki documentation")
            else:
                print(f"❌ {table_path} has no wiki documentation")
        
        if not tables_with_wiki:
            print("\n💡 No tables have wiki documentation yet.")
            print("   You can add wiki content in Dremio by:")
            print("   1. Right-clicking on a table in Dremio UI")
            print("   2. Selecting 'Edit Wiki'")
            print("   3. Adding structured documentation")
            print("   4. See wiki_examples.md for formatting guidelines")
            return
        
        # Test 2: Get detailed wiki metadata
        print(f"\n📚 Test 2: Getting detailed wiki metadata for {tables_with_wiki[0]}")
        print("-" * 40)
        
        wiki_metadata = client.get_wiki_metadata(tables_with_wiki[0])
        if wiki_metadata:
            parsed = wiki_metadata.get('parsed_metadata', {})
            print(f"Description: {parsed.get('description', 'N/A')}")
            print(f"Business Purpose: {parsed.get('business_purpose', 'N/A')}")
            print(f"Data Source: {parsed.get('data_source', 'N/A')}")
            print(f"Owner: {parsed.get('owner', 'N/A')}")
            print(f"Tags: {', '.join(parsed.get('tags', []))}")
            
            if parsed.get('column_descriptions'):
                print("Column Descriptions:")
                for col, desc in list(parsed['column_descriptions'].items())[:3]:
                    print(f"  - {col}: {desc}")
        
        # Test 3: Search wiki content
        print(f"\n🔍 Test 3: Searching wiki content")
        print("-" * 40)
        
        search_terms = ['customer', 'sales', 'product', 'order', 'account']
        for term in search_terms:
            results = client.search_wiki_content(term)
            if results:
                print(f"Found {len(results)} tables with '{term}' in wiki content:")
                for result in results[:2]:  # Show first 2 results
                    print(f"  - {result['path']}: {result['wiki_snippet'][:100]}...")
            else:
                print(f"No tables found with '{term}' in wiki content")
        
        # Test 4: AI agent with wiki context
        print(f"\n🤖 Test 4: AI agent using wiki metadata")
        print("-" * 40)
        
        test_queries = [
            "show me demographic details",
            "what tables contain customer information",
            "tell me about the sales data",
            "how many accounts are there"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            try:
                result = await agent.process_query(query)
                if result.get('success'):
                    if 'formatted_response' in result:
                        print("✅ Response with wiki metadata:")
                        print(result['formatted_response'][:200] + "...")
                    elif 'message' in result:
                        print("✅ Response:")
                        print(result['message'][:200] + "...")
                    else:
                        print("✅ Query processed successfully")
                else:
                    print(f"❌ Query failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Wiki integration test completed!")
        
        if tables_with_wiki:
            print(f"\n✅ Found {len(tables_with_wiki)} tables with wiki documentation")
            print("The AI agent can now use this rich metadata for better query generation!")
        else:
            print("\n💡 Consider adding wiki documentation to your tables for enhanced AI capabilities")
            print("See wiki_examples.md for examples and best practices")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_wiki_functionality())
