#!/usr/bin/env python3
"""
Test script to verify entity ID resolution for DataMesh tables
"""

import os
import logging
from dotenv import load_dotenv
from dremio_client import DremioClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv()

def test_entity_id_resolution():
    """Test entity ID resolution for DataMesh tables"""
    print("🔍 Testing Entity ID Resolution")
    print("=" * 40)
    
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
        
        # Get DataMesh tables
        tables = client.list_tables()
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        
        if not datamesh_tables:
            print("❌ No DataMesh tables found")
            return
        
        print(f"📋 Found {len(datamesh_tables)} DataMesh tables")
        
        # Test entity ID resolution for first few tables
        test_tables = datamesh_tables[:3]
        print(f"\n🔍 Testing entity ID resolution:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\nTesting: {table_path}")
            
            # Test entity ID resolution
            entity_id = client._get_entity_id_by_path(table_path)
            if entity_id:
                print(f"   ✅ Entity ID found: {entity_id}")
                
                # Test wiki access with this ID
                wiki_url = f"{client.api_v3}/catalog/{entity_id}/collaboration/wiki"
                try:
                    response = client.session.get(wiki_url)
                    print(f"   Wiki status: {response.status_code}")
                    
                    if response.status_code == 200:
                        wiki_data = response.json()
                        if 'text' in wiki_data and wiki_data['text']:
                            print(f"   ✅ Wiki content found: {len(wiki_data['text'])} characters")
                            print(f"   Preview: {wiki_data['text'][:100]}...")
                        else:
                            print(f"   ❌ Wiki content is empty")
                    else:
                        print(f"   ❌ Wiki not found")
                except Exception as e:
                    print(f"   ❌ Error accessing wiki: {e}")
            else:
                print(f"   ❌ No entity ID found")
        
        print(f"\n🎉 Entity ID resolution test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_entity_id_resolution()
