#!/usr/bin/env python3
"""
Test script for Anthropic Claude integration

This script tests the Anthropic API integration without requiring Dremio connection.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_anthropic_integration():
    """Test Anthropic API integration"""
    print("🧪 Testing Anthropic Claude Integration")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("💡 Please set ANTHROPIC_API_KEY in your .env file")
        return False
    
    print("✅ Anthropic API key found")
    
    try:
        from anthropic import Anthropic
        
        # Initialize client
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
        
        # Test a simple message
        print("📝 Testing Claude API with a simple query...")
        
        def _call_anthropic():
            return client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                temperature=0.1,
                messages=[{"role": "user", "content": "What is 2+2? Please respond with just the number."}]
            )
        
        response = await asyncio.to_thread(_call_anthropic)
        result = response.content[0].text.strip()
        
        print(f"✅ Claude response: {result}")
        
        if "4" in result:
            print("✅ Claude integration working correctly!")
            return True
        else:
            print("⚠️  Claude responded but with unexpected result")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        print("💡 Run: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ Anthropic API test failed: {e}")
        return False

async def test_ai_agent_with_anthropic():
    """Test AI agent with Anthropic integration"""
    print("\n🤖 Testing AI Agent with Anthropic")
    print("-" * 30)
    
    try:
        from ai_agent import DremioAIAgent
        from dremio_client import DremioClient
        
        # Create a mock client (we won't actually connect)
        config = {
            'host': 'localhost',
            'port': 9047,
            'username': 'test',
            'password': 'test',
            'use_ssl': True
        }
        
        # Create agent with Anthropic key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("❌ Cannot test AI agent - ANTHROPIC_API_KEY not found")
            return False
        
        agent = DremioAIAgent(None, anthropic_api_key=api_key)  # Pass None for client since we're not connecting
        print("✅ AI Agent initialized with Anthropic")
        
        # Test query intent analysis (doesn't require API call)
        intent = agent._analyze_query_intent("Show me all tables")
        if intent['type'] == 'table_exploration':
            print("✅ Query intent analysis working")
        else:
            print("⚠️  Query intent analysis may have issues")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Anthropic Claude Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Anthropic API Test", test_anthropic_integration),
        ("AI Agent Test", test_ai_agent_with_anthropic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
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
        print("🎉 All Anthropic integration tests passed!")
        print("\nYour setup is ready to use Claude for AI-powered data queries.")
        print("\nNext steps:")
        print("1. Configure your Dremio connection in .env")
        print("2. Try interactive mode: python cli.py interactive")
        print("3. Ask natural language questions about your data!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Set ANTHROPIC_API_KEY in your .env file")
        print("2. Install anthropic: pip install anthropic")
        print("3. Check your Anthropic API key is valid")

if __name__ == "__main__":
    asyncio.run(main())
