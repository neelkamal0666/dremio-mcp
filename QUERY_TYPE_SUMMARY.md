# 📊 Flask API Query Types - Complete Summary

## 🎯 **6 Query Types with JSON Examples**

### 1. **🔢 Count Queries**
**Purpose**: Get record counts without returning data
**Keywords**: "how many", "count", "total number"

**Example Request:**
```json
{"question": "how many accounts are there"}
```

**Example Response:**
```json
{
  "success": true,
  "query_type": "count_query",
  "data": {
    "rows": [{"total_count": 150}],
    "is_count_query": true,
    "count_value": 150,
    "message": "Total count: 150"
  }
}
```

---

### 2. **🧮 Aggregation Queries**
**Purpose**: Calculate statistics (SUM, AVG, MIN, MAX, STATS)
**Keywords**: "sum", "average", "maximum", "statistics"

**Example Request:**
```json
{"question": "what is the average age of users"}
```

**Example Response:**
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [{"avg_age": 32.5}],
    "aggregation_type": "AVG",
    "message": "Aggregation results for AVG"
  }
}
```

**Statistics Response:**
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [{
      "record_count": 150,
      "average_age": 32.5,
      "min_age": 18,
      "max_age": 65,
      "total_age": 4875
    }],
    "aggregation_type": "STATS"
  }
}
```

---

### 3. **🎯 Field Selection Queries**
**Purpose**: Return only specific columns, not all data
**Keywords**: "only the", "just the", "specific fields"

**Example Request:**
```json
{"question": "show me only the names and emails"}
```

**Example Response:**
```json
{
  "success": true,
  "query_type": "field_selection_query",
  "data": {
    "rows": [
      {"name": "John Doe", "email": "john@example.com"},
      {"name": "Jane Smith", "email": "jane@example.com"}
    ],
    "selected_columns": ["name", "email"],
    "message": "Selected fields: name, email"
  }
}
```

---

### 4. **📋 Table Exploration Queries**
**Purpose**: Discover available tables and data sources
**Keywords**: "show tables", "list data", "what tables"

**Example Request:**
```json
{"question": "show me all tables"}
```

**Example Response:**
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
    "message": "Found 3 tables matching your query"
  }
}
```

---

### 5. **📖 Metadata Request Queries**
**Purpose**: Get table structure and descriptions
**Keywords**: "describe", "structure", "explain", "metadata"

**Example Request:**
```json
{"question": "describe the accounts table"}
```

**Example Response:**
```json
{
  "success": true,
  "query_type": "metadata_request",
  "data": {
    "table_name": "DataMesh.application.accounts",
    "schema": [
      {"column_name": "id", "data_type": "INTEGER"},
      {"column_name": "name", "data_type": "VARCHAR"},
      {"column_name": "email", "data_type": "VARCHAR"}
    ],
    "wiki_description": "# Accounts Table\nThis table contains...",
    "column_count": 3
  }
}
```

---

### 6. **📊 Data Queries**
**Purpose**: Return full data records (all columns)
**Keywords**: "show me", "get data", "sample", "examples"

**Example Request:**
```json
{"question": "show me top 10 accounts"}
```

**Example Response:**
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 25,
        "created_date": "2024-01-15T10:30:00Z"
      }
    ],
    "row_count": 1,
    "columns": ["id", "name", "email", "age", "created_date"],
    "column_types": {
      "id": "int64",
      "name": "object",
      "email": "object",
      "age": "int64",
      "created_date": "datetime64[ns]"
    },
    "message": "Found 1 rows"
  }
}
```

---

## ❌ **Error Response Examples**

### **Table Not Found:**
```json
{
  "success": false,
  "error": "Could not determine which table to query",
  "error_code": "TABLE_NOT_FOUND"
}
```

### **Columns Not Found:**
```json
{
  "success": false,
  "error": "No matching columns found. Available columns: ['id', 'name', 'email']",
  "error_code": "COLUMNS_NOT_FOUND"
}
```

### **SQL Generation Failed:**
```json
{
  "success": false,
  "error": "Could not generate SQL query from your question",
  "error_code": "SQL_GENERATION_FAILED"
}
```

---

## 🔍 **Response Field Reference**

### **Common Fields (All Responses):**
- **`success`**: Boolean - Request success status
- **`query_type`**: String - Detected query type
- **`data`**: Object - Main response data
- **`error`**: String - Error message (errors only)
- **`error_code`**: String - Error code (errors only)

### **Data Object Fields:**
- **`rows`**: Array - Data records
- **`row_count`**: Number - Number of rows
- **`columns`**: Array - Column names
- **`column_types`**: Object - Column data types
- **`message`**: String - Human-readable description

### **Query-Specific Fields:**
- **`is_count_query`**: Boolean - Count query indicator
- **`count_value`**: Number - Actual count value
- **`aggregation_type`**: String - Type of aggregation
- **`selected_columns`**: Array - Specifically selected columns
- **`total_count`**: Number - Total matching items
- **`all_tables_count`**: Number - Total available tables

---

## 🧪 **Testing Examples**

### **Count Query:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "how many users are there"}'
```

### **Aggregation Query:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the total revenue"}'
```

### **Field Selection Query:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me only the names and emails"}'
```

### **Table Exploration:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "what tables are available"}'
```

### **Metadata Request:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "describe the accounts table"}'
```

### **Data Query:**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me top 10 customers"}'
```

---

## 🎯 **Query Type Detection**

| Query Type | Keywords | Example Question |
|------------|----------|------------------|
| **Count** | "how many", "count" | "how many users are there" |
| **Aggregation** | "sum", "average", "maximum" | "what is the total revenue" |
| **Field Selection** | "only the", "just the" | "show me only names and emails" |
| **Table Exploration** | "show tables", "list data" | "what tables are available" |
| **Metadata** | "describe", "structure" | "explain the accounts table" |
| **Data** | "show me", "get data" | "show me top 10 customers" |

---

## 🚀 **Performance Benefits**

### **Efficient Responses:**
- **Count Queries**: Only numbers, no data rows
- **Field Selection**: Only requested columns
- **Aggregations**: Single calculated values
- **Metadata**: Structure info only

### **Network Optimization:**
- **Reduced Payload**: Smaller JSON responses
- **Faster Queries**: Targeted SQL generation
- **Bandwidth Savings**: Only necessary data
- **Mobile Friendly**: Lightweight responses

---

## 🎉 **Summary**

Your Flask API now supports **6 intelligent query types** that automatically detect user intent and return optimized JSON responses:

1. **🔢 Count Queries** - Get numbers without data
2. **🧮 Aggregation Queries** - Calculate statistics
3. **🎯 Field Selection Queries** - Return specific columns
4. **📋 Table Exploration** - Discover data sources
5. **📖 Metadata Requests** - Get table structure
6. **📊 Data Queries** - Return full records

Each query type provides **optimized responses** that are perfect for different use cases like dashboards, reports, data exploration, and application development! 🚀
