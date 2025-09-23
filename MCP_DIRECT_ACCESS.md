# 🔧 Direct MCP Server Access Guide

## 🎯 **Yes! You can call the MCP server directly in multiple ways:**

### **1. Interactive CLI Mode (Recommended)**
```bash
# Start interactive mode
python cli.py interactive

# Then ask questions directly:
Dremio AI: show me all tables
Dremio AI: how many accounts are there
Dremio AI: what is the average age of users
```

### **2. Direct Python Script**
```python
#!/usr/bin/env python3
"""Direct MCP server access example"""

from dremio_client import DremioClient
from ai_agent import DremioAIAgent
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Create Dremio config
config = {
    'host': os.getenv('DREMIO_HOST'),
    'username': os.getenv('DREMIO_USERNAME'),
    'password': os.getenv('DREMIO_PASSWORD'),
    'verify_ssl': False
}

# Initialize client and AI agent
client = DremioClient(config)
client.authenticate()

ai_agent = DremioAIAgent(client)
ai_agent.set_openai_key(os.getenv('OPENAI_API_KEY'))

# Ask questions directly
questions = [
    "show me all tables",
    "how many accounts are there",
    "what is the average age of users",
    "show me only the names and emails"
]

for question in questions:
    print(f"\n🔍 Question: {question}")
    try:
        response = ai_agent.process_query(question)
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
```

### **3. MCP Server Tools Direct Access**
```python
#!/usr/bin/env python3
"""Direct MCP tools access"""

from dremio_mcp_server import DremioMCPServer
import asyncio

async def test_mcp_tools():
    # Initialize MCP server
    server = DremioMCPServer()
    
    # Test individual tools
    tools = [
        "query_dremio",
        "get_table_schema", 
        "list_tables",
        "search_tables",
        "get_wiki_description",
        "get_wiki_metadata",
        "search_wiki_content"
    ]
    
    for tool in tools:
        print(f"\n🔧 Testing tool: {tool}")
        try:
            if tool == "query_dremio":
                result = await server._query_dremio("SELECT COUNT(*) FROM DataMesh.application.accounts")
            elif tool == "list_tables":
                result = await server._list_tables()
            elif tool == "get_table_schema":
                result = await server._get_table_schema("DataMesh.application.accounts")
            # Add more tool tests as needed
            
            print(f"✅ {tool}: {result}")
        except Exception as e:
            print(f"❌ {tool}: {e}")

# Run the test
asyncio.run(test_mcp_tools())
```

### **4. Command Line Direct Access**
```bash
# Test connection
python cli.py test-connection

# Run a specific query
python cli.py query --query "SELECT COUNT(*) FROM DataMesh.application.accounts"

# Interactive mode
python cli.py interactive
```

## 🚀 **Quick Start Examples**

### **Example 1: Simple Direct Access**
```python
#!/usr/bin/env python3
"""Simple MCP server direct access"""

import asyncio
from dremio_mcp_server import DremioMCPServer

async def main():
    # Create MCP server instance
    server = DremioMCPServer()
    
    # Ask questions directly
    questions = [
        "show me all tables",
        "how many accounts are there",
        "what is the structure of the accounts table"
    ]
    
    for question in questions:
        print(f"\n🔍 Question: {question}")
        try:
            # Process the question
            result = await server._process_query(question)
            print(f"✅ Answer: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")

# Run it
asyncio.run(main())
```

### **Example 2: Direct Tool Access**
```python
#!/usr/bin/env python3
"""Direct MCP tool access"""

import asyncio
from dremio_mcp_server import DremioMCPServer

async def test_tools():
    server = DremioMCPServer()
    
    # Test specific tools
    print("🔧 Testing MCP tools...")
    
    # List tables
    tables = await server._list_tables()
    print(f"📋 Tables: {tables}")
    
    # Get table schema
    schema = await server._get_table_schema("DataMesh.application.accounts")
    print(f"📊 Schema: {schema}")
    
    # Query data
    result = await server._query_dremio("SELECT COUNT(*) as total FROM DataMesh.application.accounts")
    print(f"🔢 Count: {result}")
    
    # Get wiki description
    wiki = await server._get_wiki_description("DataMesh.application.accounts")
    print(f"📖 Wiki: {wiki}")

asyncio.run(test_tools())
```

## 🧪 **Testing MCP Server Directly**

### **Test Script:**
```bash
# Create test script
cat > test_mcp_direct.py << 'EOF'
#!/usr/bin/env python3
"""Test MCP server direct access"""

import asyncio
from dremio_mcp_server import DremioMCPServer

async def test_mcp():
    print("🚀 Testing MCP Server Direct Access")
    print("=" * 50)
    
    try:
        # Initialize MCP server
        server = DremioMCPServer()
        print("✅ MCP Server initialized")
        
        # Test connection
        tables = await server._list_tables()
        print(f"✅ Connection successful: Found {len(tables)} tables")
        
        # Test query
        result = await server._query_dremio("SELECT COUNT(*) as total FROM DataMesh.application.accounts")
        print(f"✅ Query successful: {result}")
        
        # Test wiki
        wiki = await server._get_wiki_description("DataMesh.application.accounts")
        print(f"✅ Wiki access: {len(wiki) if wiki else 0} characters")
        
        print("\n🎉 All MCP server tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
EOF

# Run the test
python test_mcp_direct.py
```

## 🔧 **MCP Server Tools Available**

### **Core Tools:**
- `query_dremio` - Execute SQL queries
- `get_table_schema` - Get table structure
- `list_tables` - List all tables
- `search_tables` - Search for tables
- `get_wiki_description` - Get table wiki
- `get_wiki_metadata` - Get wiki metadata
- `search_wiki_content` - Search wiki content

### **Direct Access Methods:**
```python
# Initialize server
server = DremioMCPServer()

# Access tools directly
await server._query_dremio("SELECT * FROM table")
await server._list_tables()
await server._get_table_schema("table_name")
await server._get_wiki_description("table_name")
```

## 🎯 **Use Cases for Direct Access**

### **1. Custom Applications:**
```python
# Build your own interface
class MyDataApp:
    def __init__(self):
        self.mcp_server = DremioMCPServer()
    
    async def ask_question(self, question):
        return await self.mcp_server._process_query(question)
    
    async def get_tables(self):
        return await self.mcp_server._list_tables()
```

### **2. Batch Processing:**
```python
# Process multiple questions
questions = [
    "how many users are there",
    "what is the average age",
    "show me all tables"
]

for question in questions:
    result = await server._process_query(question)
    print(f"Q: {question}\nA: {result}\n")
```

### **3. Integration Testing:**
```python
# Test MCP server functionality
async def test_mcp_integration():
    server = DremioMCPServer()
    
    # Test all tools
    tools_to_test = [
        ("_list_tables", []),
        ("_query_dremio", ["SELECT COUNT(*) FROM DataMesh.application.accounts"]),
        ("_get_table_schema", ["DataMesh.application.accounts"])
    ]
    
    for tool, args in tools_to_test:
        try:
            result = await getattr(server, tool)(*args)
            print(f"✅ {tool}: {result}")
        except Exception as e:
            print(f"❌ {tool}: {e}")
```

## 🚀 **Quick Start Commands**

```bash
# Interactive mode (easiest)
python cli.py interactive

# Test connection
python cli.py test-connection

# Run specific query
python cli.py query --query "SELECT COUNT(*) FROM DataMesh.application.accounts"

# Test MCP server directly
python test_mcp_direct.py
```

## 🎉 **Summary**

**Yes! You can call the MCP server directly in multiple ways:**

1. **Interactive CLI**: `python cli.py interactive`
2. **Direct Python**: Import and use MCP server class
3. **Command Line**: `python cli.py query --query "SQL"`
4. **Custom Scripts**: Build your own interfaces

The MCP server provides **direct access to all Dremio functionality** through Python code! 🚀
