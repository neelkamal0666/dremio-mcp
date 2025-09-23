#!/usr/bin/env python3
"""
Simple startup script for Flask API
Uses environment variables for configuration
"""

import os
import sys
from dotenv import load_dotenv
from flask_api import DremioFlaskAPI

def main():
    """Start Flask API with environment configuration"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    dremio_host = os.getenv('DREMIO_HOST')
    dremio_username = os.getenv('DREMIO_USERNAME')
    dremio_password = os.getenv('DREMIO_PASSWORD')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not all([dremio_host, dremio_username, dremio_password]):
        print("❌ Missing required environment variables:")
        print("   DREMIO_HOST, DREMIO_USERNAME, DREMIO_PASSWORD")
        print("\nPlease check your .env file or set these variables.")
        return 1
    
    # Create Dremio config
    config = {
        'host': dremio_host,
        'username': dremio_username,
        'password': dremio_password,
        'verify_ssl': os.getenv('DREMIO_VERIFY_SSL', 'true').lower() == 'true',
        'cert_path': os.getenv('DREMIO_CERT_PATH'),
        'flight_port': int(os.getenv('DREMIO_FLIGHT_PORT', '32010')),
        'default_source': os.getenv('DREMIO_DEFAULT_SOURCE'),
        'default_schema': os.getenv('DREMIO_DEFAULT_SCHEMA')
    }
    
    # Create Flask API
    api = DremioFlaskAPI()
    
    # Initialize Dremio connection
    print("🔌 Connecting to Dremio...")
    if not api.initialize_dremio_connection(config):
        print("❌ Failed to connect to Dremio")
        return 1
    print("✅ Connected to Dremio")
    
    # Initialize AI agent if OpenAI key is provided
    if openai_key:
        print("🤖 Initializing AI agent...")
        if api.initialize_ai_agent(openai_key):
            print("✅ AI agent initialized")
        else:
            print("⚠️  AI agent initialization failed, continuing without AI features")
    else:
        print("⚠️  No OpenAI API key provided, using heuristic SQL generation")
    
    # Get server configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"\n🚀 Starting Flask API server on {host}:{port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 API will be available at: http://{host}:{port}")
    print("\n📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /tables - List all tables")
    print("   POST /query - Process natural language queries")
    print("   GET  /table/<name>/metadata - Get table metadata")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    try:
        # Run the server
        api.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
