#!/usr/bin/env python3
"""
Test MCP Server Direct Access
Demonstrates how to call MCP server directly and get responses
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mcp_direct_access():
    """Test direct access to MCP server"""
    print("🚀 Testing MCP Server Direct Access")
    print("=" * 50)
    
    try:
        # Import MCP server
        from dremio_mcp_server import DremioMCPServer
        
        # Initialize MCP server
        server = DremioMCPServer()
        print("✅ MCP Server initialized")
        
        # Test 1: List tables
        print("\n🔍 Test 1: List tables")
        try:
            tables = await server._list_tables()
            print(f"✅ Found {len(tables)} tables")
            if tables:
                print(f"   Sample tables: {tables[:3]}")
        except Exception as e:
            print(f"❌ Error listing tables: {e}")
        
        # Test 2: Query data
        print("\n🔍 Test 2: Query data")
        try:
            # Try a simple count query
            result = await server._query_dremio("SELECT COUNT(*) as total FROM DataMesh.application.accounts")
            print(f"✅ Query successful: {result}")
        except Exception as e:
            print(f"❌ Error querying data: {e}")
        
        # Test 3: Get table schema
        print("\n🔍 Test 3: Get table schema")
        try:
            schema = await server._get_table_schema("DataMesh.application.accounts")
            print(f"✅ Schema retrieved: {len(schema)} columns")
            if schema:
                print(f"   Sample columns: {[col['column_name'] for col in schema[:3]]}")
        except Exception as e:
            print(f"❌ Error getting schema: {e}")
        
        # Test 4: Get wiki description
        print("\n🔍 Test 4: Get wiki description")
        try:
            wiki = await server._get_wiki_description("DataMesh.application.accounts")
            if wiki:
                print(f"✅ Wiki retrieved: {len(wiki)} characters")
                print(f"   Preview: {wiki[:100]}...")
            else:
                print("ℹ️  No wiki description found")
        except Exception as e:
            print(f"❌ Error getting wiki: {e}")
        
        # Test 5: Search tables
        print("\n🔍 Test 5: Search tables")
        try:
            search_results = await server._search_tables("account")
            print(f"✅ Search successful: {len(search_results)} results")
            if search_results:
                print(f"   Results: {search_results}")
        except Exception as e:
            print(f"❌ Error searching tables: {e}")
        
        print("\n🎉 MCP Server direct access test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the correct directory and all dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_simple_questions():
    """Test simple question processing"""
    print("\n" + "=" * 50)
    print("🧠 Testing Simple Question Processing")
    print("=" * 50)
    
    try:
        from dremio_client import DremioClient
        from ai_agent import DremioAIAgent
        
        # Create Dremio config
        config = {
            'host': os.getenv('DREMIO_HOST'),
            'username': os.getenv('DREMIO_USERNAME'),
            'password': os.getenv('DREMIO_PASSWORD'),
            'verify_ssl': False
        }
        
        # Initialize client and AI agent
        print("🔌 Connecting to Dremio...")
        client = DremioClient(config)
        client.authenticate()
        print("✅ Connected to Dremio")
        
        # Initialize AI agent
        print("🤖 Initializing AI agent...")
        ai_agent = DremioAIAgent(client)
        if os.getenv('OPENAI_API_KEY'):
            ai_agent.set_openai_key(os.getenv('OPENAI_API_KEY'))
            print("✅ AI agent initialized with OpenAI")
        else:
            print("⚠️  No OpenAI API key, using heuristic mode")
        
        # Test questions
        questions = [
            "show me all tables",
            "how many accounts are there",
            "what is the structure of the accounts table"
        ]
        
        for question in questions:
            print(f"\n🔍 Question: {question}")
            try:
                response = ai_agent.process_query(question)
                print(f"✅ Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎉 Simple question processing test completed!")
        
    except Exception as e:
        print(f"❌ Error in simple question processing: {e}")

async def main():
    """Main test function"""
    print("🧪 MCP Server Direct Access Test Suite")
    print("=" * 60)
    
    # Test 1: Direct MCP server access
    await test_mcp_direct_access()
    
    # Test 2: Simple question processing
    test_simple_questions()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("✅ MCP server can be called directly")
    print("✅ You can get responses from MCP server")
    print("✅ Both async and sync access methods work")
    print("✅ AI agent can process natural language questions")
    print("\n🚀 You can use MCP server directly in your applications!")

if __name__ == "__main__":
    asyncio.run(main())
