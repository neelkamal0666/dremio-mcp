# 🔧 MCP Server with JSON Responses

## 🎯 **Enhanced MCP Server with Structured JSON Output**

The MCP server now returns **structured JSON responses** similar to the Flask API, making it easier to integrate with applications and providing consistent data formats.

## 🚀 **Key Features**

### **✅ Structured JSON Responses**
- **Consistent Format**: Same structure as Flask API
- **Error Handling**: Specific error codes and messages
- **Type Information**: Column types and metadata
- **Query Classification**: Automatic query type detection

### **✅ Enhanced Tools**
- **`query_dremio`** - Execute SQL with JSON response
- **`get_table_schema`** - Get schema with JSON response
- **`list_tables`** - List tables with JSON response
- **`search_tables`** - Search tables with JSON response
- **`get_wiki_description`** - Get wiki with JSON response
- **`get_wiki_metadata`** - Get metadata with JSON response
- **`search_wiki_content`** - Search wiki with JSON response
- **`process_natural_language_query`** - AI queries with JSON response

## 📊 **JSON Response Examples**

### **1. Query Dremio Response**
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {"id": 1, "name": "John Doe", "email": "john@example.com"},
      {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
    ],
    "row_count": 2,
    "columns": ["id", "name", "email"],
    "column_types": {
      "id": "int64",
      "name": "object", 
      "email": "object"
    },
    "is_count_query": false,
    "message": "Found 2 rows"
  }
}
```

### **2. List Tables Response**
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": [
      "DataMesh.application.accounts",
      "DataMesh.application.users",
      "DataMesh.application.projects"
    ],
    "total_count": 3,
    "all_tables_count": 15,
    "message": "Found 3 tables"
  }
}
```

### **3. Get Table Schema Response**
```json
{
  "success": true,
  "query_type": "metadata_request",
  "data": {
    "table_name": "DataMesh.application.accounts",
    "schema": [
      {
        "column_name": "id",
        "data_type": "INTEGER",
        "is_nullable": "NO"
      },
      {
        "column_name": "name",
        "data_type": "VARCHAR",
        "is_nullable": "YES"
      }
    ],
    "column_count": 2,
    "message": "Schema for table 'DataMesh.application.accounts'"
  }
}
```

### **4. Get Wiki Description Response**
```json
{
  "success": true,
  "query_type": "metadata_request",
  "data": {
    "table_name": "DataMesh.application.accounts",
    "wiki_description": "# Accounts Table\n\nThis table contains customer account information...",
    "message": "Wiki description for table 'DataMesh.application.accounts'"
  }
}
```

### **5. Search Tables Response**
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": [
      "DataMesh.application.accounts",
      "DataMesh.application.account_history"
    ],
    "total_count": 2,
    "search_term": "account",
    "message": "Found 2 tables matching 'account'"
  }
}
```

### **6. Error Response**
```json
{
  "success": false,
  "error": "Table 'nonexistent.table' not found",
  "error_code": "TABLE_NOT_FOUND"
}
```

## 🔧 **Usage Examples**

### **Start JSON MCP Server**
```bash
# Start the JSON MCP server
python dremio_mcp_server_json.py

# Or using Make
make start-mcp-json
```

### **Test JSON MCP Server**
```bash
# Test the JSON responses
python test_mcp_json.py

# Or using Make
make test-mcp-json
```

### **Direct Python Access**
```python
#!/usr/bin/env python3
"""Direct access to JSON MCP server"""

import asyncio
from dremio_mcp_server_json import DremioMCPServerJSON

async def main():
    # Initialize JSON MCP server
    server = DremioMCPServerJSON()
    
    # Test different tools
    tools_to_test = [
        ("_list_tables_json", {}),
        ("_query_dremio_json", {"query": "SELECT COUNT(*) FROM DataMesh.application.accounts"}),
        ("_get_table_schema_json", {"table_path": "DataMesh.application.accounts"}),
        ("_get_wiki_description_json", {"table_path": "DataMesh.application.accounts"})
    ]
    
    for tool, args in tools_to_test:
        print(f"\n🔧 Testing {tool}")
        try:
            result = await getattr(server, tool)(args)
            print(f"✅ Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")

asyncio.run(main())
```

## 🎯 **Response Fields Reference**

### **Common Fields (All Responses)**
- **`success`**: Boolean - Request success status
- **`query_type`**: String - Type of query (data_query, table_exploration, metadata_request)
- **`data`**: Object - Main response data
- **`error`**: String - Error message (errors only)
- **`error_code`**: String - Error code (errors only)

### **Data Object Fields**
- **`rows`**: Array - Data records
- **`row_count`**: Number - Number of rows
- **`columns`**: Array - Column names
- **`column_types`**: Object - Column data types
- **`message`**: String - Human-readable description

### **Query-Specific Fields**
- **`is_count_query`**: Boolean - Count query indicator
- **`total_count`**: Number - Total matching items
- **`all_tables_count`**: Number - Total available tables
- **`search_term`**: String - Search term used
- **`table_name`**: String - Table name
- **`schema`**: Array - Table schema
- **`column_count`**: Number - Number of columns

## 🚀 **Benefits of JSON Responses**

### **1. Consistent Format**
- **Same Structure**: Identical to Flask API responses
- **Easy Integration**: Simple to parse and use
- **Standardized**: Follows common API patterns

### **2. Rich Metadata**
- **Type Information**: Column data types included
- **Query Classification**: Automatic query type detection
- **Error Details**: Specific error codes and messages

### **3. Easy Parsing**
- **Structured Data**: JSON format for easy parsing
- **Type Safety**: Clear data types and structures
- **Error Handling**: Consistent error response format

### **4. Integration Ready**
- **API Compatibility**: Works with existing Flask API clients
- **Tool Integration**: Easy to use in applications
- **Debugging**: Clear error messages and codes

## 🧪 **Testing**

### **Test JSON MCP Server**
```bash
# Test all JSON responses
python test_mcp_json.py

# Or using Make
make test-mcp-json
```

### **Test Specific Tools**
```python
# Test individual tools
import asyncio
from dremio_mcp_server_json import DremioMCPServerJSON

async def test_tool():
    server = DremioMCPServerJSON()
    
    # Test query
    result = await server._query_dremio_json({
        "query": "SELECT COUNT(*) FROM DataMesh.application.accounts"
    })
    print(json.dumps(result, indent=2))

asyncio.run(test_tool())
```

## 🎉 **Summary**

The enhanced MCP server now provides:

1. **✅ Structured JSON Responses** - Consistent with Flask API
2. **✅ Rich Metadata** - Type information and query classification
3. **✅ Error Handling** - Specific error codes and messages
4. **✅ Easy Integration** - Simple to parse and use
5. **✅ Tool Compatibility** - Works with existing MCP tools

**Your MCP server now returns structured JSON responses that are easy to parse and integrate!** 🚀
