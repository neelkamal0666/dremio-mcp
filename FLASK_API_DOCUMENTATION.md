# Flask REST API Documentation

## 🚀 **Overview**

The Flask REST API provides HTTP endpoints for interacting with your Dremio data using natural language queries. It handles dynamic column responses, count queries, and various data exploration scenarios.

## 📋 **Features**

- **Natural Language Processing**: Convert questions to SQL queries
- **Dynamic Column Handling**: Automatically adapts to different table schemas
- **Count Query Support**: Special handling for aggregation queries
- **Wiki Metadata Integration**: Rich context from Dremio wiki content
- **Error Handling**: Comprehensive error responses with codes
- **CORS Support**: Cross-origin requests enabled

## 🔧 **Installation & Setup**

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your Dremio and OpenAI credentials:
```bash
# Dremio Configuration
DREMIO_HOST=your-dremio-host.com
DREMIO_USERNAME=your-username
DREMIO_PASSWORD=your-password
DREMIO_VERIFY_SSL=false
DREMIO_FLIGHT_PORT=32010
DREMIO_DEFAULT_SOURCE=your-source
DREMIO_DEFAULT_SCHEMA=your-schema

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-key

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

### 3. Start the Server
```bash
# Using the startup script
python start_flask_api.py

# Or using Make
make start-flask

# Development mode
make run-flask-dev
```

## 📡 **API Endpoints**

### 1. **Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Dremio MCP Flask API",
  "version": "1.0.0"
}
```

### 2. **List Tables**
```http
GET /tables
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tables": [
      "DataMesh.application.accounts",
      "DataMesh.application.demographic_details",
      "DataMesh.application.projects"
    ],
    "count": 3
  }
}
```

### 3. **Process Natural Language Query**
```http
POST /query
Content-Type: application/json

{
  "question": "show me all tables"
}
```

**Response Types:**

#### Table Exploration Response:
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": ["DataMesh.application.accounts"],
    "total_count": 1,
    "all_tables_count": 10
  },
  "message": "Found 1 tables matching your query"
}
```

#### Data Query Response:
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      }
    ],
    "row_count": 1,
    "columns": ["id", "name", "email"],
    "column_types": {
      "id": "int64",
      "name": "object",
      "email": "object"
    },
    "is_count_query": false,
    "message": "Found 1 rows"
  }
}
```

#### Count Query Response:
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {
        "total_count": 150
      }
    ],
    "row_count": 1,
    "columns": ["total_count"],
    "column_types": {
      "total_count": "int64"
    },
    "is_count_query": true,
    "message": "Total count: 150"
  }
}
```

#### Metadata Request Response:
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
        "is_nullable": "YES"
      }
    ],
    "wiki_description": "# Accounts Table\nThis table contains...",
    "column_count": 5
  }
}
```

### 4. **Get Table Metadata**
```http
GET /table/{table_name}/metadata
```

**Example:**
```http
GET /table/DataMesh.application.accounts/metadata
```

**Response:**
```json
{
  "success": true,
  "data": {
    "table_name": "DataMesh.application.accounts",
    "schema": [
      {
        "column_name": "id",
        "data_type": "INTEGER",
        "is_nullable": "YES"
      }
    ],
    "wiki_description": "# Accounts Table\nThis table contains...",
    "column_count": 5
  }
}
```

## 🔍 **Query Types & Examples**

### 1. **Table Exploration**
```json
{
  "question": "show me all tables"
}
```

### 2. **Count Queries**
```json
{
  "question": "how many accounts are there"
}
```

### 3. **Data Queries**
```json
{
  "question": "show me top 10 accounts"
}
```

### 4. **Metadata Queries**
```json
{
  "question": "describe the accounts table"
}
```

### 5. **General Queries**
```json
{
  "question": "help me understand the data"
}
```

## ⚠️ **Error Handling**

### Error Response Format:
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes:
- `MISSING_QUESTION`: Missing question field
- `EMPTY_QUESTION`: Empty question string
- `CLIENT_NOT_INITIALIZED`: Dremio client not connected
- `SQL_GENERATION_FAILED`: Could not generate SQL
- `DATA_QUERY_ERROR`: Error executing query
- `TABLE_METADATA_ERROR`: Error getting table metadata
- `INTERNAL_ERROR`: Internal server error

## 🧪 **Testing**

### Run Test Suite:
```bash
# Test the API
python test_flask_api.py

# Or using Make
make test-flask
```

### Manual Testing with curl:
```bash
# Health check
curl http://localhost:5000/health

# List tables
curl http://localhost:5000/tables

# Process query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me all tables"}'

# Get table metadata
curl http://localhost:5000/table/DataMesh.application.accounts/metadata
```

## 🔧 **Configuration Options**

### Environment Variables:
- `DREMIO_HOST`: Dremio server host
- `DREMIO_USERNAME`: Dremio username
- `DREMIO_PASSWORD`: Dremio password
- `DREMIO_VERIFY_SSL`: SSL verification (true/false)
- `DREMIO_CERT_PATH`: Path to SSL certificate
- `DREMIO_FLIGHT_PORT`: Dremio Flight port
- `DREMIO_DEFAULT_SOURCE`: Default source
- `DREMIO_DEFAULT_SCHEMA`: Default schema
- `OPENAI_API_KEY`: OpenAI API key (optional)
- `FLASK_HOST`: Flask host (default: 0.0.0.0)
- `FLASK_PORT`: Flask port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: false)

## 🚀 **Production Deployment**

### Using Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 flask_api:DremioFlaskAPI().app
```

### Using Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "start_flask_api.py"]
```

## 📊 **Response Schema Details**

### Dynamic Column Handling:
The API automatically detects and returns:
- **Column names**: Dynamic based on table schema
- **Column types**: Pandas data types (int64, object, float64, etc.)
- **Row data**: Flexible JSON structure
- **Count queries**: Special handling for aggregation

### Count Query Detection:
The API detects count queries by keywords:
- "how many"
- "count"
- "number of"

### Table Name Resolution:
- Supports fully qualified names: `DataMesh.application.accounts`
- Supports partial names: `accounts`
- Automatic table matching based on keywords

## 🎯 **Use Cases**

1. **Data Exploration**: "show me all tables"
2. **Record Counting**: "how many users are there"
3. **Data Retrieval**: "show me top 10 customers"
4. **Schema Discovery**: "describe the accounts table"
5. **Business Intelligence**: "what tables contain customer information"

## 🔒 **Security Considerations**

- **CORS**: Enabled for cross-origin requests
- **Input Validation**: All inputs are validated
- **Error Handling**: No sensitive information in error messages
- **SSL**: Supports custom SSL certificates
- **Authentication**: Uses Dremio authentication

## 📈 **Performance**

- **Caching**: Table metadata is cached
- **Connection Pooling**: Reuses Dremio connections
- **Async Support**: Ready for async implementation
- **Memory Efficient**: Streams large result sets

## 🛠️ **Troubleshooting**

### Common Issues:
1. **Connection Errors**: Check Dremio host and credentials
2. **SSL Errors**: Set `DREMIO_VERIFY_SSL=false` for testing
3. **AI Errors**: System falls back to heuristic SQL generation
4. **Table Not Found**: Check table names and permissions

### Debug Mode:
```bash
FLASK_DEBUG=true python start_flask_api.py
```

## 📚 **Next Steps**

1. **Deploy**: Use the production deployment guide
2. **Monitor**: Add logging and monitoring
3. **Scale**: Use load balancers for high traffic
4. **Extend**: Add custom endpoints for specific needs

The Flask API provides a robust, production-ready interface for your Dremio data with natural language querying capabilities! 🎉
