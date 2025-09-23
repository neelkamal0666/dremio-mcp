# 🚀 Startup Guide - Flask API vs MCP Server

## 🏗️ **Architecture Overview**

Your Dremio MCP system has **two separate components**:

1. **Flask REST API** - HTTP endpoints for web/mobile apps
2. **MCP Server** - Model Context Protocol server for AI tools

## 🔄 **Component Relationships**

```
┌─────────────────┐    ┌─────────────────┐
│   Flask API     │    │   MCP Server    │
│   (HTTP REST)   │    │   (AI Tools)    │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌─────────────────┐
            │  Dremio Client  │
            │  (Shared Core)  │
            └─────────────────┘
```

## 🚀 **Startup Options**

### **Option 1: Flask API Only (Recommended for Web Apps)**
```bash
# Start Flask API
python start_flask_api.py

# Or using Make
make start-flask
```

**Use Case**: Web applications, mobile apps, API integrations
**Access**: HTTP endpoints at `http://localhost:5000`

### **Option 2: MCP Server Only (Recommended for AI Tools)**
```bash
# Start MCP server
python cli.py start-server

# Or using Make
make run-server
```

**Use Case**: Claude Desktop, Cursor, other MCP-compatible tools
**Access**: MCP protocol for AI agents

### **Option 3: Both Components (Full System)**
```bash
# Terminal 1: Start MCP Server
python cli.py start-server

# Terminal 2: Start Flask API
python start_flask_api.py
```

**Use Case**: Complete system with both HTTP and MCP access

## 📋 **Startup Commands Reference**

### **Flask API Commands:**
```bash
# Basic startup
python start_flask_api.py

# Development mode
FLASK_DEBUG=true python start_flask_api.py

# Using Make
make start-flask
make run-flask-dev
```

### **MCP Server Commands:**
```bash
# Start MCP server
python cli.py start-server

# Interactive mode
python cli.py interactive

# Test connection
python cli.py test-connection

# Using Make
make run-server
make run-interactive
```

## 🔧 **Configuration**

### **Shared Configuration (.env file):**
```bash
# Dremio Configuration (used by both)
DREMIO_HOST=your-dremio-host.com
DREMIO_USERNAME=your-username
DREMIO_PASSWORD=your-password
DREMIO_VERIFY_SSL=false

# OpenAI Configuration (used by both)
OPENAI_API_KEY=your-openai-key

# Flask Configuration (Flask API only)
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

### **MCP Configuration (claude_desktop_config.json):**
```json
{
  "mcpServers": {
    "dremio": {
      "command": "python",
      "args": ["/path/to/dremio_mcp_server.py"],
      "env": {
        "DREMIO_HOST": "your-dremio-host.com",
        "DREMIO_USERNAME": "your-username",
        "DREMIO_PASSWORD": "your-password"
      }
    }
  }
}
```

## 🎯 **When to Use Each Component**

### **Use Flask API When:**
- Building web applications
- Creating mobile apps
- Integrating with external systems
- Need HTTP REST endpoints
- Want to build custom UIs

### **Use MCP Server When:**
- Using Claude Desktop
- Working with Cursor
- Need AI agent integration
- Want natural language queries
- Using MCP-compatible tools

### **Use Both When:**
- Building comprehensive data platform
- Need both HTTP and AI access
- Supporting multiple user types
- Creating hybrid applications

## 🚀 **Quick Start Examples**

### **For Web Development:**
```bash
# Start Flask API
python start_flask_api.py

# Test API
curl http://localhost:5000/health
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me all tables"}'
```

### **For AI Tools:**
```bash
# Start MCP server
python cli.py start-server

# Test in Claude Desktop or Cursor
# The MCP server will be available as a tool
```

### **For Complete System:**
```bash
# Terminal 1: MCP Server
python cli.py start-server

# Terminal 2: Flask API
python start_flask_api.py

# Both are now running independently
```

## 🔍 **Verification**

### **Check Flask API:**
```bash
curl http://localhost:5000/health
# Should return: {"status": "healthy", "service": "Dremio MCP Flask API"}
```

### **Check MCP Server:**
```bash
# Check if MCP server is running
ps aux | grep dremio_mcp_server.py
# Should show the MCP server process
```

## ⚠️ **Important Notes**

1. **Independent Components**: Flask API and MCP server are separate processes
2. **Shared Core**: Both use the same Dremio client and AI agent
3. **Different Protocols**: HTTP REST vs MCP protocol
4. **Separate Ports**: Flask (5000) vs MCP (varies)
5. **Different Use Cases**: Web apps vs AI tools

## 🎉 **Summary**

- **Flask API**: HTTP REST endpoints for web/mobile apps
- **MCP Server**: AI tool integration for Claude/Cursor
- **Both**: Complete system with dual access methods
- **Startup**: Choose based on your use case
- **Configuration**: Shared Dremio settings, separate protocols

Choose the component(s) that match your use case! 🚀
