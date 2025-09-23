#!/usr/bin/env python3
"""
Test network connectivity to Anthropic API
"""

import socket
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_network_connectivity():
    """Test network connectivity to Anthropic API"""
    print("🌐 Testing Network Connectivity to Anthropic API")
    print("=" * 50)
    
    # Test 1: Basic DNS resolution
    print("1. Testing DNS resolution...")
    try:
        ip = socket.gethostbyname('api.anthropic.com')
        print(f"✅ DNS resolution successful: api.anthropic.com -> {ip}")
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return
    
    # Test 2: TCP connection
    print("\n2. Testing TCP connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('api.anthropic.com', 443))
        sock.close()
        if result == 0:
            print("✅ TCP connection to port 443 successful")
        else:
            print(f"❌ TCP connection failed with code: {result}")
            return
    except Exception as e:
        print(f"❌ TCP connection failed: {e}")
        return
    
    # Test 3: HTTPS request
    print("\n3. Testing HTTPS request...")
    try:
        response = requests.get('https://api.anthropic.com', timeout=10)
        print(f"✅ HTTPS request successful: Status {response.status_code}")
    except requests.exceptions.ConnectTimeout:
        print("❌ HTTPS request failed: Connection timeout")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ HTTPS request failed: Connection error - {e}")
    except Exception as e:
        print(f"❌ HTTPS request failed: {e}")
    
    # Test 4: Check if API key is set
    print("\n4. Checking API key...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
    else:
        print("❌ API key not found in environment variables")
    
    # Test 5: Try a simple API call with different models
    print("\n5. Testing API calls with different models...")
    if api_key:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        models_to_try = [
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022", 
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229"
        ]
        
        for model in models_to_try:
            try:
                print(f"   Trying model: {model}")
                response = client.messages.create(
                    model=model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                print(f"   ✅ {model} - Success: {response.content[0].text}")
                break
            except Exception as e:
                print(f"   ❌ {model} - Failed: {str(e)[:100]}...")

if __name__ == "__main__":
    test_network_connectivity()
