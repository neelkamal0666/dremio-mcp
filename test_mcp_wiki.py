#!/usr/bin/env python3
"""
Test script for MCP server wiki functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from dremio_mcp_server import DremioMCP, DremioConfig

# Load environment variables
load_dotenv()

async def test_mcp_wiki():
    """Test MCP server wiki functionality"""
    print("🧪 Testing MCP Server Wiki Functionality")
    print("=" * 50)
    
    try:
        # Initialize MCP server
        mcp_server = DremioMCP()
        print("✅ MCP Server initialized successfully!")
        
        # Get some DataMesh tables to test with
        tables = mcp_server.client.list_tables()
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        
        if not datamesh_tables:
            print("❌ No DataMesh tables found for testing")
            return
        
        print(f"📋 Found {len(datamesh_tables)} DataMesh tables")
        
        # Test with first DataMesh table
        schema, table = datamesh_tables[0]
        table_path = f"{schema}.{table}"
        print(f"\n🔍 Testing MCP wiki functionality with: {table_path}")
        
        # Test 1: Get wiki metadata
        print("\n📚 Test 1: Getting wiki metadata...")
        try:
            result = await mcp_server._get_wiki_metadata({"table_path": table_path})
            if result.content and result.content[0].text:
                print("✅ Wiki metadata retrieved successfully!")
                print(f"Content preview: {result.content[0].text[:200]}...")
            else:
                print("❌ No wiki metadata found")
        except Exception as e:
            print(f"❌ Error getting wiki metadata: {e}")
        
        # Test 2: Get wiki description
        print("\n📝 Test 2: Getting wiki description...")
        try:
            description = await mcp_server._get_wiki_description(table_path)
            if description and "not available" not in description.lower():
                print("✅ Wiki description retrieved successfully!")
                print(f"Description: {description[:200]}...")
            else:
                print("❌ No wiki description found")
        except Exception as e:
            print(f"❌ Error getting wiki description: {e}")
        
        # Test 3: Search wiki content
        print("\n🔍 Test 3: Searching wiki content...")
        try:
            result = await mcp_server._search_wiki_content({"search_term": "account"})
            if result.content and result.content[0].text:
                print("✅ Wiki search completed successfully!")
                print(f"Results: {result.content[0].text[:200]}...")
            else:
                print("❌ No wiki search results found")
        except Exception as e:
            print(f"❌ Error searching wiki content: {e}")
        
        print(f"\n🎉 MCP wiki functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_wiki())
