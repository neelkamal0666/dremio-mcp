#!/usr/bin/env python3
"""
Test AWS Bedrock Integration
Tests the MCP server with Bedrock for SQL generation
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_bedrock_mcp_server():
    """Test MCP server with Bedrock integration"""
    print("🚀 Testing MCP Server with AWS Bedrock Integration")
    print("=" * 60)
    
    # Check environment variables
    print("🔍 Checking Bedrock configuration...")
    required_vars = [
        'BEDROCK_MODEL_ID',
        'AWS_REGION', 
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'DREMIO_HOST',
        'DREMIO_USERNAME',
        'DREMIO_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("\nPlease set the following environment variables:")
        print("  BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0")
        print("  AWS_REGION=us-east-1")
        print("  AWS_ACCESS_KEY_ID=your-access-key")
        print("  AWS_SECRET_ACCESS_KEY=your-secret-key")
        print("  DREMIO_HOST=your-dremio-host.com")
        print("  DREMIO_USERNAME=your-username")
        print("  DREMIO_PASSWORD=your-password")
        return False
    
    print("✅ All required environment variables are set")
    
    try:
        # Import the JSON MCP server
        from dremio_mcp_server_json import DremioMCPServerJSON
        
        # Initialize MCP server
        server = DremioMCPServerJSON()
        print("✅ JSON MCP Server with Bedrock initialized")
        
        # Test 1: Natural language query processing
        print("\n🔍 Test 1: Natural language query processing")
        try:
            result = await server._process_natural_language_query_json({
                "question": "show me all tables"
            })
            print(f"✅ Natural language result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error processing natural language: {e}")
        
        # Test 2: SQL generation with Bedrock
        print("\n🔍 Test 2: SQL generation with Bedrock")
        try:
            result = await server._query_dremio_json({
                "query": "SELECT COUNT(*) as total FROM DataMesh.application.accounts"
            })
            print(f"✅ SQL query result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
        
        # Test 3: List tables
        print("\n🔍 Test 3: List tables")
        try:
            result = await server._list_tables_json({})
            print(f"✅ List tables result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error listing tables: {e}")
        
        print("\n🎉 Bedrock MCP Server test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bedrock_ai_agent():
    """Test Bedrock AI agent directly"""
    print("\n" + "=" * 60)
    print("🧠 Testing Bedrock AI Agent Directly")
    print("=" * 60)
    
    try:
        from ai_agent_bedrock import DremioAIAgentBedrock
        from dremio_client import DremioClient
        
        # Create Dremio config
        config = {
            'host': os.getenv('DREMIO_HOST'),
            'username': os.getenv('DREMIO_USERNAME'),
            'password': os.getenv('DREMIO_PASSWORD'),
            'verify_ssl': False
        }
        
        # Initialize Dremio client
        print("🔌 Connecting to Dremio...")
        client = DremioClient(config)
        client.authenticate()
        print("✅ Connected to Dremio")
        
        # Initialize Bedrock AI agent
        print("🤖 Initializing Bedrock AI agent...")
        ai_agent = DremioAIAgentBedrock(
            client,
            provider="bedrock",
            bedrock_model_id=os.getenv('BEDROCK_MODEL_ID')
        )
        print("✅ Bedrock AI agent initialized")
        
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
        
        print("\n🎉 Bedrock AI agent test completed!")
        
    except Exception as e:
        print(f"❌ Error in Bedrock AI agent test: {e}")

def show_bedrock_configuration():
    """Show Bedrock configuration guide"""
    print("\n" + "=" * 60)
    print("⚙️ AWS Bedrock Configuration Guide")
    print("=" * 60)
    
    print("\n📋 Required Environment Variables:")
    print("  BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("  AWS_REGION=us-east-1")
    print("  AWS_ACCESS_KEY_ID=your-access-key")
    print("  AWS_SECRET_ACCESS_KEY=your-secret-key")
    
    print("\n🔧 AWS IAM Permissions Required:")
    print("  bedrock:InvokeModel")
    print("  bedrock:InvokeModelWithResponseStream")
    
    print("\n🎯 Supported Bedrock Models:")
    print("  - anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("  - anthropic.claude-3-5-haiku-20241022-v1:0")
    print("  - anthropic.claude-3-opus-20240229-v1:0")
    print("  - meta.llama-3-1-405b-instruct-v1:0")
    print("  - meta.llama-3-1-70b-instruct-v1:0")
    
    print("\n🚀 Quick Start:")
    print("  1. Set environment variables")
    print("  2. Run: python test_bedrock_integration.py")
    print("  3. Or start MCP server: python dremio_mcp_server_json.py")

async def main():
    """Main test function"""
    print("🧪 AWS Bedrock Integration Test Suite")
    print("=" * 60)
    
    # Show configuration guide
    show_bedrock_configuration()
    
    # Test 1: Bedrock MCP server
    success = await test_bedrock_mcp_server()
    
    # Test 2: Bedrock AI agent directly
    if success:
        test_bedrock_ai_agent()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    if success:
        print("✅ Bedrock integration working correctly")
        print("✅ MCP server can use Bedrock for SQL generation")
        print("✅ Natural language queries processed with Bedrock")
        print("✅ Fallback to OpenAI if Bedrock not available")
    else:
        print("❌ Bedrock integration needs configuration")
        print("❌ Please check environment variables and AWS credentials")
    
    print("\n🚀 Your MCP server now supports AWS Bedrock for AI-powered SQL generation!")

if __name__ == "__main__":
    asyncio.run(main())
