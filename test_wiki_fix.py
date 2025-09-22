#!/usr/bin/env python3
"""
Simple test script to verify wiki fix
"""

import os
import logging
from dotenv import load_dotenv
from dremio_client import DremioClient

# Set logging level to INFO to reduce noise
logging.basicConfig(level=logging.INFO)

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
        
        # Get DataMesh tables specifically
        tables = client.list_tables()
        if not tables:
            print("❌ No tables found")
            return
        
        # Filter for DataMesh tables
        datamesh_tables = [(schema, table) for schema, table in tables if 'DataMesh' in schema or 'datamesh' in schema.lower()]
        
        if not datamesh_tables:
            print("❌ No DataMesh tables found. Available schemas:")
            schemas = set([schema for schema, table in tables[:20]])
            for schema in sorted(schemas):
                print(f"   - {schema}")
            return
        
        # Test with DataMesh tables
        test_tables = datamesh_tables[:5]
        print(f"\n📋 Testing wiki API with {len(test_tables)} DataMesh tables:")
        
        for schema, table in test_tables:
            table_path = f"{schema}.{table}"
            print(f"\n🔍 Testing: {table_path}")
            
            # Test the new wiki metadata method
            wiki_metadata = client.get_wiki_metadata(table_path)
            if wiki_metadata and wiki_metadata.get('raw_text'):
                print(f"   ✅ Wiki content found: {len(wiki_metadata['raw_text'])} characters")
                print(f"   Preview: {wiki_metadata['raw_text'][:100]}...")
                
                # Show parsed metadata if available
                parsed = wiki_metadata.get('parsed_metadata', {})
                if parsed:
                    print(f"   📋 Parsed metadata:")
                    if parsed.get('description'):
                        print(f"     Description: {parsed['description'][:50]}...")
                    if parsed.get('business_purpose'):
                        print(f"     Purpose: {parsed['business_purpose'][:50]}...")
                    if parsed.get('tags'):
                        print(f"     Tags: {', '.join(parsed['tags'])}")
                    if parsed.get('column_descriptions'):
                        col_count = len(parsed['column_descriptions'])
                        print(f"     Column descriptions: {col_count} columns documented")
            else:
                print(f"   ❌ No wiki content found")
                
                # Try to get basic wiki description as fallback
                wiki_description = client.get_wiki_description(table_path)
                if wiki_description:
                    print(f"   ✅ Basic wiki description found: {len(wiki_description)} characters")
                    print(f"   Preview: {wiki_description[:100]}...")
                else:
                    print(f"   ❌ No wiki description found either")
        
        print(f"\n🎉 Wiki fix test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_wiki_fix()
