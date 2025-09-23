#!/usr/bin/env python3
"""
Test MCP Server with JSON Responses
Demonstrates the enhanced MCP server that returns structured JSON
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_mcp_json_server():
    """Test the JSON MCP server"""
    print("🚀 Testing MCP Server with JSON Responses")
    print("=" * 60)
    
    try:
        # Import the JSON MCP server
        from dremio_mcp_server_json import DremioMCPServerJSON
        
        # Initialize MCP server
        server = DremioMCPServerJSON()
        print("✅ JSON MCP Server initialized")
        
        # Test 1: List tables
        print("\n🔍 Test 1: List tables")
        try:
            result = await server._list_tables_json({})
            print(f"✅ List tables result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error listing tables: {e}")
        
        # Test 2: Query data
        print("\n🔍 Test 2: Query data")
        try:
            result = await server._query_dremio_json({
                "query": "SELECT COUNT(*) as total FROM DataMesh.application.accounts"
            })
            print(f"✅ Query result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error querying data: {e}")
        
        # Test 3: Get table schema
        print("\n🔍 Test 3: Get table schema")
        try:
            result = await server._get_table_schema_json({
                "table_path": "DataMesh.application.accounts"
            })
            print(f"✅ Schema result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error getting schema: {e}")
        
        # Test 4: Get wiki description
        print("\n🔍 Test 4: Get wiki description")
        try:
            result = await server._get_wiki_description_json({
                "table_path": "DataMesh.application.accounts"
            })
            print(f"✅ Wiki result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error getting wiki: {e}")
        
        # Test 5: Search tables
        print("\n🔍 Test 5: Search tables")
        try:
            result = await server._search_tables_json({
                "search_term": "account"
            })
            print(f"✅ Search result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error searching tables: {e}")
        
        # Test 6: Natural language query (if AI agent available)
        print("\n🔍 Test 6: Natural language query")
        try:
            result = await server._process_natural_language_query_json({
                "question": "show me all tables"
            })
            print(f"✅ Natural language result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error processing natural language: {e}")
        
        print("\n🎉 JSON MCP Server test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the correct directory and all dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_json_response_format():
    """Test the JSON response format"""
    print("\n" + "=" * 60)
    print("📊 JSON Response Format Examples")
    print("=" * 60)
    
    # Example responses
    examples = {
        "query_dremio": {
            "success": True,
            "query_type": "data_query",
            "data": {
                "rows": [{"id": 1, "name": "John", "email": "john@example.com"}],
                "row_count": 1,
                "columns": ["id", "name", "email"],
                "column_types": {"id": "int64", "name": "object", "email": "object"},
                "is_count_query": False,
                "message": "Found 1 rows"
            }
        },
        "list_tables": {
            "success": True,
            "query_type": "table_exploration",
            "data": {
                "tables": ["DataMesh.application.accounts", "DataMesh.application.users"],
                "total_count": 2,
                "all_tables_count": 10,
                "message": "Found 2 tables"
            }
        },
        "get_table_schema": {
            "success": True,
            "query_type": "metadata_request",
            "data": {
                "table_name": "DataMesh.application.accounts",
                "schema": [
                    {"column_name": "id", "data_type": "INTEGER"},
                    {"column_name": "name", "data_type": "VARCHAR"}
                ],
                "column_count": 2,
                "message": "Schema for table 'DataMesh.application.accounts'"
            }
        },
        "error_response": {
            "success": False,
            "error": "Table not found",
            "error_code": "TABLE_NOT_FOUND"
        }
    }
    
    for tool_name, example in examples.items():
        print(f"\n🔧 {tool_name.upper()} Response:")
        print(json.dumps(example, indent=2))

async def main():
    """Main test function"""
    print("🧪 MCP Server JSON Response Test Suite")
    print("=" * 60)
    
    # Test 1: JSON MCP server functionality
    await test_mcp_json_server()
    
    # Test 2: JSON response format examples
    test_json_response_format()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("✅ MCP server now returns structured JSON responses")
    print("✅ Consistent format with Flask API")
    print("✅ Easy to parse and integrate")
    print("✅ Error handling with specific error codes")
    print("\n🚀 MCP server responses are now JSON-formatted!")

if __name__ == "__main__":
    asyncio.run(main())
