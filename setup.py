#!/usr/bin/env python3
"""
Setup script for Dremio MCP Server and AI Agent

This script helps with initial setup and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("⚙️  Setting up environment configuration...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy example to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from template")
    
    print("\n📝 Please edit .env file with your Dremio connection details:")
    print("   - DREMIO_HOST: Your Dremio server hostname")
    print("   - DREMIO_USERNAME: Your Dremio username")
    print("   - DREMIO_PASSWORD: Your Dremio password")
    print("   - ANTHROPIC_API_KEY: (Optional) Your Anthropic API key for enhanced features")
    
    return True

def test_connection():
    """Test connection to Dremio"""
    print("\n🔗 Testing connection to Dremio...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup first.")
        return False
    
    try:
        result = subprocess.run([sys.executable, "cli.py", "test-connection"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Connection test successful!")
            return True
        else:
            print("❌ Connection test failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection test timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def create_claude_config():
    """Create Claude Desktop configuration"""
    print("\n🤖 Creating Claude Desktop configuration...")
    
    config_file = Path("claude_desktop_config.json")
    if config_file.exists():
        print("✅ Claude Desktop config already exists")
        return True
    
    # Get current directory
    current_dir = Path.cwd().absolute()
    
    config_content = f"""{{
  "mcpServers": {{
    "dremio": {{
      "command": "python",
      "args": ["{current_dir}/dremio_mcp_server.py"],
      "env": {{
        "DREMIO_HOST": "your-dremio-host.com",
        "DREMIO_PORT": "9047",
        "DREMIO_USERNAME": "your-username",
        "DREMIO_PASSWORD": "your-password",
        "DREMIO_USE_SSL": "true",
        "DREMIO_VERIFY_SSL": "true",
        "ANTHROPIC_API_KEY": "your-anthropic-api-key"
      }}
    }}
  }}
}}"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print("✅ Created claude_desktop_config.json")
    print("\n📝 To use with Claude Desktop:")
    print("1. Copy the contents of claude_desktop_config.json")
    print("2. Add it to your Claude Desktop configuration")
    print("3. Update the environment variables with your actual values")
    print("4. Restart Claude Desktop")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Dremio MCP Server and AI Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create Claude config
    create_claude_config()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your Dremio connection details")
    print("2. Test connection: python cli.py test-connection")
    print("3. Try interactive mode: python cli.py interactive")
    print("4. Run example: python example_usage.py")
    print("5. Start MCP server: python cli.py start-server")
    
    # Ask if user wants to test connection
    try:
        test_now = input("\nWould you like to test the connection now? (y/n): ").lower().strip()
        if test_now in ['y', 'yes']:
            test_connection()
    except KeyboardInterrupt:
        print("\nSetup completed. You can test the connection later.")

if __name__ == "__main__":
    main()
