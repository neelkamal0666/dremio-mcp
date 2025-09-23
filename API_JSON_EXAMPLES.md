# 📊 Flask API JSON Output Examples

## 🎯 **Complete JSON Response Examples for All Query Types**

### 1. **🔢 Count Query Response**

**Request:**
```json
{
  "question": "how many accounts are there"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "count_query",
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
    "count_value": 150,
    "message": "Total count: 150"
  }
}
```

**Alternative Count Response:**
```json
{
  "success": true,
  "query_type": "count_query",
  "data": {
    "rows": [
      {
        "record_count": 42
      }
    ],
    "row_count": 1,
    "columns": ["record_count"],
    "column_types": {
      "record_count": "int64"
    },
    "is_count_query": true,
    "count_value": 42,
    "message": "Total count: 42"
  }
}
```

---

### 2. **🧮 Aggregation Query Response**

**Request:**
```json
{
  "question": "what is the average age of users"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [
      {
        "avg_age": 32.5
      }
    ],
    "row_count": 1,
    "columns": ["avg_age"],
    "column_types": {
      "avg_age": "float64"
    },
    "aggregation_type": "AVG",
    "message": "Aggregation results for AVG"
  }
}
```

**Statistics Query Response:**
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [
      {
        "record_count": 150,
        "average_age": 32.5,
        "min_age": 18,
        "max_age": 65,
        "total_age": 4875
      }
    ],
    "row_count": 1,
    "columns": ["record_count", "average_age", "min_age", "max_age", "total_age"],
    "column_types": {
      "record_count": "int64",
      "average_age": "float64",
      "min_age": "int64",
      "max_age": "int64",
      "total_age": "int64"
    },
    "aggregation_type": "STATS",
    "message": "Aggregation results for STATS"
  }
}
```

**Sum Query Response:**
```json
{
  "success": true,
  "query_type": "aggregation_query",
  "data": {
    "rows": [
      {
        "sum_revenue": 125000.50
      }
    ],
    "row_count": 1,
    "columns": ["sum_revenue"],
    "column_types": {
      "sum_revenue": "float64"
    },
    "aggregation_type": "SUM",
    "message": "Aggregation results for SUM"
  }
}
```

---

### 3. **🎯 Field Selection Query Response**

**Request:**
```json
{
  "question": "show me only the names and emails"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "field_selection_query",
  "data": {
    "rows": [
      {
        "name": "John Doe",
        "email": "john.doe@example.com"
      },
      {
        "name": "Jane Smith",
        "email": "jane.smith@example.com"
      },
      {
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com"
      }
    ],
    "row_count": 3,
    "columns": ["name", "email"],
    "column_types": {
      "name": "object",
      "email": "object"
    },
    "selected_columns": ["name", "email"],
    "message": "Selected fields: name, email"
  }
}
```

**ID and Age Selection Response:**
```json
{
  "success": true,
  "query_type": "field_selection_query",
  "data": {
    "rows": [
      {
        "id": 1,
        "age": 25
      },
      {
        "id": 2,
        "age": 30
      },
      {
        "id": 3,
        "age": 35
      }
    ],
    "row_count": 3,
    "columns": ["id", "age"],
    "column_types": {
      "id": "int64",
      "age": "int64"
    },
    "selected_columns": ["id", "age"],
    "message": "Selected fields: id, age"
  }
}
```

---

### 4. **📋 Table Exploration Response**

**Request:**
```json
{
  "question": "show me all tables"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": [
      "DataMesh.application.accounts",
      "DataMesh.application.demographic_details",
      "DataMesh.application.projects",
      "DataMesh.application.tags",
      "DataMesh.application.users"
    ],
    "total_count": 5,
    "all_tables_count": 15,
    "message": "Found 5 tables matching your query"
  }
}
```

**Filtered Table Response:**
```json
{
  "success": true,
  "query_type": "table_exploration",
  "data": {
    "tables": [
      "DataMesh.application.accounts",
      "DataMesh.application.users"
    ],
    "total_count": 2,
    "all_tables_count": 15,
    "message": "Found 2 tables matching your query"
  }
}
```

---

### 5. **📖 Metadata Request Response**

**Request:**
```json
{
  "question": "describe the accounts table"
}
```

**Response:**
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
      },
      {
        "column_name": "email",
        "data_type": "VARCHAR",
        "is_nullable": "YES"
      },
      {
        "column_name": "age",
        "data_type": "INTEGER",
        "is_nullable": "YES"
      },
      {
        "column_name": "created_date",
        "data_type": "TIMESTAMP",
        "is_nullable": "YES"
      }
    ],
    "wiki_description": "# Accounts Table\n\nThis table contains customer account information including personal details and contact information.\n\n## Business Purpose\nStores core customer data for account management and user authentication.\n\n## Key Fields\n- **id**: Unique customer identifier\n- **name**: Customer full name\n- **email**: Primary contact email\n- **age**: Customer age for demographic analysis\n- **created_date**: Account creation timestamp",
    "column_count": 5
  }
}
```

**No Wiki Description Response:**
```json
{
  "success": true,
  "query_type": "metadata_request",
  "data": {
    "table_name": "DataMesh.application.projects",
    "schema": [
      {
        "column_name": "project_id",
        "data_type": "INTEGER",
        "is_nullable": "NO"
      },
      {
        "column_name": "project_name",
        "data_type": "VARCHAR",
        "is_nullable": "YES"
      }
    ],
    "wiki_description": null,
    "column_count": 2
  }
}
```

---

### 6. **📊 Data Query Response**

**Request:**
```json
{
  "question": "show me top 10 accounts"
}
```

**Response:**
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 25,
        "created_date": "2024-01-15T10:30:00Z"
      },
      {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "age": 30,
        "created_date": "2024-01-16T14:20:00Z"
      },
      {
        "id": 3,
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "age": 35,
        "created_date": "2024-01-17T09:15:00Z"
      }
    ],
    "row_count": 3,
    "columns": ["id", "name", "email", "age", "created_date"],
    "column_types": {
      "id": "int64",
      "name": "object",
      "email": "object",
      "age": "int64",
      "created_date": "datetime64[ns]"
    },
    "is_count_query": false,
    "message": "Found 3 rows"
  }
}
```

**Large Dataset Response:**
```json
{
  "success": true,
  "query_type": "data_query",
  "data": {
    "rows": [
      {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
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

---

## ❌ **Error Response Examples**

### **Table Not Found Error:**
```json
{
  "success": false,
  "error": "Could not determine which table to query",
  "error_code": "TABLE_NOT_FOUND"
}
```

### **Columns Not Found Error:**
```json
{
  "success": false,
  "error": "No matching columns found. Available columns: ['id', 'name', 'email', 'age']",
  "error_code": "COLUMNS_NOT_FOUND"
}
```

### **SQL Generation Failed Error:**
```json
{
  "success": false,
  "error": "Could not generate SQL query from your question",
  "error_code": "SQL_GENERATION_FAILED"
}
```

### **Internal Server Error:**
```json
{
  "success": false,
  "error": "Internal server error: Connection timeout",
  "error_code": "INTERNAL_ERROR"
}
```

---

## 🔍 **Response Field Explanations**

### **Common Fields:**
- **`success`**: Boolean indicating if the request was successful
- **`query_type`**: The detected type of query (count_query, aggregation_query, etc.)
- **`data`**: The main response data object
- **`error`**: Error message (only present when success=false)
- **`error_code`**: Specific error code for debugging

### **Data Object Fields:**
- **`rows`**: Array of data records (varies by query type)
- **`row_count`**: Number of rows returned
- **`columns`**: Array of column names
- **`column_types`**: Object mapping column names to pandas data types
- **`message`**: Human-readable description of the results

### **Query-Specific Fields:**
- **`is_count_query`**: Boolean for count queries
- **`count_value`**: The actual count number
- **`aggregation_type`**: Type of aggregation (SUM, AVG, etc.)
- **`selected_columns`**: Array of specifically selected columns
- **`total_count`**: Total number of matching items
- **`all_tables_count`**: Total number of available tables

---

## 🧪 **Testing the API**

### **Using curl:**
```bash
# Count query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "how many accounts are there"}'

# Aggregation query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the average age"}'

# Field selection query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "show me only the names and emails"}'
```

### **Using Python:**
```python
import requests

response = requests.post('http://localhost:5000/query', 
                        json={'question': 'how many users are there'})
data = response.json()
print(f"Count: {data['data']['count_value']}")
```

These JSON examples show the complete structure and variety of responses your Flask API can provide for different query types! 🎉
