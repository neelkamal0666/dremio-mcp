#!/usr/bin/env python3
"""
Test SSL fix with proper environment setup
"""

import os
import ssl
import urllib3
import warnings
from dotenv import load_dotenv
from anthropic import Anthropic

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Set SSL environment variables
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Load environment variables
load_dotenv()

async def test_ssl_fix():
    """Test SSL fix with proper configuration"""
    print("🔧 Testing SSL Fix")
    print("=" * 30)
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize client
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized")
        
        # Test with a simple request
        print("Testing API call...")
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        
        print(f"✅ API call successful: {response.content[0].text}")
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        # Try alternative approach
        print("\nTrying alternative SSL configuration...")
        try:
            import ssl
            import httpx
            
            # Create custom SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # This won't work with Anthropic client directly, but shows the approach
            print("Note: Anthropic client doesn't support custom SSL context directly")
            print("You may need to use a different network or contact IT for corporate certificates")
            
        except Exception as e2:
            print(f"Alternative approach also failed: {e2}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ssl_fix())
