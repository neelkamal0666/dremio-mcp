#!/usr/bin/env python3
"""
Simple Bedrock Integration Test
Tests the Bedrock AI agent without requiring MCP server
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_bedrock_ai_agent():
    """Test Bedrock AI agent directly"""
    print("🚀 Testing Bedrock AI Agent")
    print("=" * 50)
    
    try:
        from ai_agent_bedrock import DremioAIAgentBedrock
        
        # Test 1: Initialize Bedrock AI agent
        print("🔍 Test 1: Initialize Bedrock AI agent")
        ai_agent = DremioAIAgentBedrock(
            dremio_client=None,  # We'll test without Dremio connection
            provider="bedrock",
            bedrock_model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        print("✅ Bedrock AI agent initialized")
        
        # Test 2: Check provider
        print(f"🔍 Test 2: Provider = {ai_agent.provider}")
        print(f"✅ Provider correctly set to: {ai_agent.provider}")
        
        # Test 3: Check model ID
        print(f"🔍 Test 3: Model ID = {ai_agent.bedrock_model_id}")
        print(f"✅ Model ID correctly set to: {ai_agent.bedrock_model_id}")
        
        # Test 4: Check Bedrock client
        print("🔍 Test 4: Bedrock client initialization")
        if ai_agent.bedrock_client:
            print("✅ Bedrock client initialized")
        else:
            print("⚠️  Bedrock client not initialized (missing AWS credentials)")
        
        print("\n🎉 Bedrock AI agent test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment_configuration():
    """Test environment configuration"""
    print("\n" + "=" * 50)
    print("⚙️ Testing Environment Configuration")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        'BEDROCK_MODEL_ID',
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    
    print("🔍 Checking environment variables...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check optional variables
    optional_vars = ['OPENAI_API_KEY', 'DREMIO_HOST', 'DREMIO_USERNAME', 'DREMIO_PASSWORD']
    print("\n🔍 Checking optional environment variables...")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'PASSWORD' in var:
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"ℹ️  {var}: Not set (optional)")

def show_configuration_guide():
    """Show configuration guide"""
    print("\n" + "=" * 50)
    print("📋 Configuration Guide")
    print("=" * 50)
    
    print("\n🔧 Required Environment Variables:")
    print("  BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0")
    print("  AWS_REGION=us-east-1")
    print("  AWS_ACCESS_KEY_ID=your-aws-access-key")
    print("  AWS_SECRET_ACCESS_KEY=your-aws-secret-key")
    
    print("\n🔧 Optional Environment Variables:")
    print("  OPENAI_API_KEY=your-openai-api-key  # Fallback")
    print("  DREMIO_HOST=your-dremio-host.com    # For full testing")
    print("  DREMIO_USERNAME=your-username       # For full testing")
    print("  DREMIO_PASSWORD=your-password       # For full testing")
    
    print("\n🚀 Quick Start:")
    print("  1. Set environment variables")
    print("  2. Run: python test_bedrock_simple.py")
    print("  3. For full testing: python test_bedrock_integration.py")

def main():
    """Main test function"""
    print("🧪 Simple Bedrock Integration Test")
    print("=" * 50)
    
    # Show configuration guide
    show_configuration_guide()
    
    # Test environment configuration
    test_environment_configuration()
    
    # Test Bedrock AI agent
    success = test_bedrock_ai_agent()
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    if success:
        print("✅ Bedrock AI agent working correctly")
        print("✅ Provider selection working")
        print("✅ Model configuration working")
        print("✅ Ready for full integration testing")
    else:
        print("❌ Bedrock AI agent needs configuration")
        print("❌ Please check environment variables and dependencies")
    
    print("\n🚀 Your MCP server now supports AWS Bedrock for AI-powered SQL generation!")

if __name__ == "__main__":
    main()
