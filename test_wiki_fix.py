#!/usr/bin/env python3
"""
Simple test script to verify wiki fix
"""

import os
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def test_wiki_fix():
    """Test the wiki fix"""
    print("🧪 Testing Wiki Fix")
    print("=" * 30)
    
    # Configuration
    config = {
        'host': os.getenv('DREMIO_HOST', 'localhost'),
        'port': int(os.getenv('DREMIO_PORT', '9047')),
        'username': os.getenv('DREMIO_USERNAME', ''),
        'password': os.getenv('DREMIO_PASSWORD', ''),
        'use_ssl': os.getenv('DREMIO_USE_SSL', 'true').lower() == 'true',
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true'
    }
    
    try:
        # Initialize client
        client = DremioClient(config)
        if not client.authenticate():
            print("❌ Failed to authenticate with Dremio")
            return
        
        print("✅ Successfully connected to Dremio!")
        
        # Get a sample table to test with
        tables = client.list_tables()
        if not tables:
            print("❌ No tables found")
            return
        
        # Test with first few tables
        test_tables = tables[:5]
        print(f"\n📋 Testing wiki API with {len(test_tables)} tables:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\n🔍 Testing: {table_path}")
            
            # Test the new wiki metadata method
            wiki_metadata = client.get_wiki_metadata(table_path)
            if wiki_metadata and wiki_metadata.get('raw_text'):
                print(f"   ✅ Wiki content found: {len(wiki_metadata['raw_text'])} characters")
                print(f"   Preview: {wiki_metadata['raw_text'][:100]}...")
            else:
                print(f"   ❌ No wiki content found")
        
        print(f"\n🎉 Wiki fix test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_wiki_fix()
