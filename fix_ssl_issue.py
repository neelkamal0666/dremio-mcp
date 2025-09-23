#!/usr/bin/env python3
"""
Script to help fix SSL certificate issues with Anthropic API
"""

import os
import ssl
import urllib3
from dotenv import load_dotenv

def fix_ssl_issues():
    """Provide solutions for SSL certificate issues"""
    print("🔧 SSL Certificate Issue Fix")
    print("=" * 40)
    
    print("The issue is: SSL certificate verification failure")
    print("This is common in corporate environments with proxy servers.")
    print()
    
    print("SOLUTIONS:")
    print("1. Set environment variable to disable SSL verification:")
    print("   export PYTHONHTTPSVERIFY=0")
    print("   export CURL_CA_BUNDLE=")
    print()
    
    print("2. Or add to your .env file:")
    print("   PYTHONHTTPSVERIFY=0")
    print("   CURL_CA_BUNDLE=")
    print()
    
    print("3. For corporate environments, you may need to:")
    print("   - Contact IT to get the corporate CA certificate")
    print("   - Set REQUESTS_CA_BUNDLE environment variable")
    print("   - Or use a VPN that doesn't intercept SSL traffic")
    print()
    
    print("4. Alternative: Use a different network (mobile hotspot)")
    print()
    
    # Try to apply the fix
    print("Applying SSL workaround...")
    try:
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Set environment variables
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        
        print("✅ SSL workaround applied")
        print("Note: This disables SSL verification - use only in trusted environments")
        
    except Exception as e:
        print(f"❌ Failed to apply SSL workaround: {e}")

if __name__ == "__main__":
    fix_ssl_issues()
