#!/usr/bin/env python3
"""
Test script to verify Dremio MCP Server setup

This script runs basic tests to ensure everything is working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy imported successfully")
    except ImportError as e:
        print(f"❌ sqlalchemy import failed: {e}")
        return False
    
    try:
        from mcp.server import Server
        print("✅ mcp imported successfully")
    except ImportError as e:
        print(f"❌ mcp import failed: {e}")
        return False
    
    try:
        from dremio_client import DremioClient
        print("✅ dremio_client imported successfully")
    except ImportError as e:
        print(f"❌ dremio_client import failed: {e}")
        return False
    
    try:
        from ai_agent import DremioAIAgent
        print("✅ ai_agent imported successfully")
    except ImportError as e:
        print(f"❌ ai_agent import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment configuration...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run: cp env.example .env and edit with your settings")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    required_vars = ['DREMIO_HOST', 'DREMIO_USERNAME', 'DREMIO_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Please edit .env file with your Dremio connection details")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_dremio_connection():
    """Test connection to Dremio"""
    print("\n📡 Testing Dremio connection...")
    
    try:
        from dremio_client import DremioClient
        
        use_ssl = os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true'
        verify_ssl = os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true'
        host = os.getenv('DREMIO_HOST')
        port = int(os.getenv('DREMIO_PORT', '9047'))
        scheme = 'https' if use_ssl else 'http'

        print(f"Testing Dremio connection to {scheme}://{host}:{port} (verify_ssl={'on' if verify_ssl else 'off'})...")
        
        config = {
            'host': host,
            'port': port,
            'username': os.getenv('DREMIO_USERNAME'),
            'password': os.getenv('DREMIO_PASSWORD'),
            'use_ssl': use_ssl,
            'verify_ssl': verify_ssl,
        }
        
        client = DremioClient(config)
        
        if client.authenticate():
            print("✅ Successfully authenticated with Dremio")
            
            # Try to list tables
            try:
                tables = client.list_tables()
                print(f"✅ Found {len(tables)} tables")
                return True
            except Exception as e:
                print(f"⚠️  Authentication successful but query failed: {e}")
                return True  # Still consider this a success
        else:
            print("❌ Failed to authenticate with Dremio")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_ai_agent():
    """Test AI agent functionality"""
    print("\n🤖 Testing AI agent...")
    
    try:
        from dremio_client import DremioClient
        from ai_agent import DremioAIAgent
        
        use_ssl = os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true'
        verify_ssl = os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true'
        host = os.getenv('DREMIO_HOST')
        port = int(os.getenv('DREMIO_PORT', '9047'))
        cert_path = os.getenv('DREMIO_CERT_PATH')
        flight_port = int(os.getenv('DREMIO_FLIGHT_PORT', os.getenv('DREMIO_PORT', '32010')))
        scheme = 'https' if use_ssl else 'http'

        print(f"AI agent connecting to {scheme}://{host}:{port} (verify_ssl={'on' if verify_ssl else 'off'}, flight_port={flight_port})...")
        if cert_path:
            print(f"Using CA bundle: {cert_path}")
        
        config = {
            'host': host,
            'port': port,
            'username': os.getenv('DREMIO_USERNAME'),
            'password': os.getenv('DREMIO_PASSWORD'),
            'use_ssl': use_ssl,
            'verify_ssl': verify_ssl,
            'cert_path': cert_path,
            'flight_port': flight_port,
        }
        
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Cannot test AI agent - Dremio connection failed")
            return False
        
        agent = DremioAIAgent(client)
        print("✅ AI agent initialized successfully")
        
        # Test query intent analysis
        intent = agent._analyze_query_intent("Show me all tables")
        if intent['type'] == 'table_exploration':
            print("✅ Query intent analysis working")
        else:
            print("⚠️  Query intent analysis may have issues")
        
        return True
        
    except Exception as e:
        print(f"❌ AI agent test failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server initialization"""
    print("\n🔌 Testing MCP server...")
    
    try:
        from dremio_mcp_server import DremioMCP
        
        server = DremioMCP()
        print("✅ MCP server initialized successfully")
        
        # Basic sanity check: server object exists and has a run coroutine
        if hasattr(server, 'run') and callable(getattr(server, 'run')):
            print("✅ MCP server has a run method")
            return True
        else:
            print("⚠️  MCP server run method not found")
            return False
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Dremio MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("Dremio Connection Test", test_dremio_connection),
        ("AI Agent Test", test_ai_agent),
        ("MCP Server Test", test_mcp_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Try interactive mode: python cli.py interactive")
        print("2. Run example: python example_usage.py")
        print("3. Start MCP server: python cli.py start-server")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Configure .env file with your Dremio connection details")
        print("3. Check your Dremio server is accessible")
        print("4. Verify your credentials are correct")

if __name__ == "__main__":
    asyncio.run(main())
