#!/usr/bin/env python3
"""
Simple test to verify wiki fix works
"""

import os
from dotenv import load_dotenv
from dremio_client import DremioClient

# Load environment variables
load_dotenv()

def test_wiki_simple():
    """Simple test for wiki functionality"""
    print("🧪 Simple Wiki Test")
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
        
        # Test with one DataMesh table
        test_table = "DataMesh.application.accounts"
        print(f"\n🔍 Testing: {test_table}")
        
        # Test wiki metadata
        try:
            wiki_metadata = client.get_wiki_metadata(test_table)
            if wiki_metadata and wiki_metadata.get('raw_text'):
                print(f"✅ Wiki content found: {len(wiki_metadata['raw_text'])} characters")
                print(f"Preview: {wiki_metadata['raw_text'][:100]}...")
            else:
                print("❌ No wiki content found")
        except Exception as e:
            print(f"❌ Error getting wiki metadata: {e}")
        
        # Test wiki description
        try:
            wiki_description = client.get_wiki_description(test_table)
            if wiki_description:
                print(f"✅ Wiki description found: {len(wiki_description)} characters")
                print(f"Preview: {wiki_description[:100]}...")
            else:
                print("❌ No wiki description found")
        except Exception as e:
            print(f"❌ Error getting wiki description: {e}")
        
        print(f"\n🎉 Simple wiki test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_wiki_simple()
