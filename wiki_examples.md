# Dremio Wiki Metadata Examples

This document provides examples of how to structure wiki content in Dremio to maximize the effectiveness of the AI agent and MCP server.

## Recommended Wiki Structure

### Basic Table Documentation

```markdown
# Customer Data Table

This table contains customer information including demographics, contact details, and account status.

## Business Purpose
Stores core customer data for CRM, marketing, and customer service operations.

## Data Source
**Source:** Salesforce CRM
**Update Frequency:** Daily at 2 AM EST
**Owner:** Data Engineering Team

## Column Descriptions
- customer_id: Unique identifier for each customer
- first_name: Customer's first name
- last_name: Customer's last name
- email: Primary email address for communication
- phone: Primary phone number
- date_of_birth: Customer's birth date for age calculations
- address: Full mailing address
- city: Customer's city
- state: Customer's state/province
- zip_code: Postal/ZIP code
- country: Customer's country
- registration_date: When customer first registered
- last_login: Most recent login timestamp
- account_status: Active, Inactive, Suspended, or Closed
- customer_tier: Bronze, Silver, Gold, or Platinum based on spending

## Usage Notes
- Use customer_id as the primary key for joins
- account_status should be checked before sending marketing emails
- customer_tier is calculated monthly based on total spending

## Data Quality Notes
- Email addresses are validated for format
- Phone numbers are standardized to international format
- Some historical records may have missing zip_code data
```

### Sales Data Documentation

```markdown
# Sales Transactions

Daily sales transaction data from all channels including online, retail, and wholesale.

## Business Purpose
Track all sales activities for revenue reporting, customer analysis, and inventory management.

## Data Source
**Source:** Multiple systems (Shopify, POS, B2B Portal)
**Update Frequency:** Real-time for online, hourly for retail
**Owner:** Sales Operations Team

## Column Descriptions
- transaction_id: Unique transaction identifier
- customer_id: Links to customer table (can be null for guest purchases)
- product_id: Links to product catalog
- quantity: Number of units sold
- unit_price: Price per unit at time of sale
- total_amount: Total transaction value (quantity × unit_price)
- discount_amount: Total discount applied
- tax_amount: Tax calculated for the transaction
- channel: Online, Retail, Wholesale, or Mobile
- payment_method: Credit Card, PayPal, Cash, Check, etc.
- transaction_date: Date and time of the transaction
- sales_rep_id: ID of sales representative (for B2B sales)
- region: Geographic region where sale occurred

## Usage Notes
- Use transaction_date for time-based analysis
- channel field helps segment sales by channel
- customer_id is null for guest purchases
- total_amount = (quantity × unit_price) - discount_amount + tax_amount

## Data Quality Notes
- All transactions have valid product_id references
- Negative quantities indicate returns/refunds
- Some historical data may have missing sales_rep_id
```

### Product Catalog Documentation

```markdown
# Product Catalog

Master product information including pricing, categories, and inventory status.

## Business Purpose
Central repository for all product information used across sales, marketing, and inventory systems.

## Data Source
**Source:** Product Information Management (PIM) system
**Update Frequency:** Daily sync at 6 AM EST
**Owner:** Product Management Team

## Column Descriptions
- product_id: Unique product identifier (SKU)
- product_name: Display name of the product
- description: Detailed product description
- category_id: Links to product category hierarchy
- brand: Product brand/manufacturer
- model_number: Manufacturer's model number
- color: Primary color of the product
- size: Product size (varies by category)
- weight: Product weight in pounds
- dimensions: Product dimensions (L×W×H in inches)
- cost_price: Wholesale cost from supplier
- retail_price: Standard retail price
- sale_price: Current sale price (null if not on sale)
- inventory_quantity: Current stock level
- reorder_point: Minimum stock level before reordering
- is_active: Whether product is currently available for sale
- launch_date: When product was first introduced
- discontinued_date: When product was discontinued (null if active)

## Usage Notes
- Use is_active flag to filter current products
- sale_price overrides retail_price when not null
- inventory_quantity is updated in real-time
- category_id links to product category hierarchy

## Data Quality Notes
- All active products have valid category_id
- Discontinued products have discontinued_date set
- Some legacy products may have missing dimensions
```

## Advanced Wiki Features

### Using Tags and Categories

```markdown
# Financial Data

## Tags
#finance #accounting #monthly #revenue

## Business Purpose
Monthly financial reporting data for revenue recognition and accounting.

## Data Source
**Source:** ERP System (SAP)
**Update Frequency:** Monthly on the 5th business day
**Owner:** Finance Team
```

### Data Quality Documentation

```markdown
# Customer Demographics

## Data Quality Notes
- Age calculations based on date_of_birth may be off by 1 day due to timezone differences
- Some customers have multiple addresses - this table shows the primary address
- Email validation was implemented in 2020, older records may have invalid formats
- Phone numbers are standardized but some international numbers may be incomplete
```

### Usage Guidelines

```markdown
# Marketing Campaign Data

## Usage Notes
- campaign_id is the primary key for all marketing activities
- Use campaign_type to filter by email, social, display, etc.
- conversion_date is null for campaigns without conversions
- cost_per_click is only available for digital campaigns
- Always join with customer table to get demographic information

## Common Queries
- Campaign performance by type: GROUP BY campaign_type
- ROI calculation: (revenue - cost) / cost
- Customer acquisition cost: total_cost / new_customers
```

## Best Practices

### 1. Consistent Structure
- Always include Business Purpose and Data Source
- Use consistent column description format
- Include update frequency and ownership information

### 2. Business Context
- Explain why the data exists
- Describe how it's used in business processes
- Include any business rules or calculations

### 3. Technical Details
- Document data types and constraints
- Explain relationships to other tables
- Note any data quality issues or limitations

### 4. Usage Examples
- Provide common query patterns
- Include calculation formulas
- Document best practices for data access

### 5. Maintenance
- Keep documentation up to date
- Review and update quarterly
- Include change history for major updates

## AI Agent Benefits

With properly structured wiki content, the AI agent can:

1. **Understand Business Context**: Know why data exists and how it's used
2. **Generate Better Queries**: Use proper column names and business logic
3. **Provide Rich Metadata**: Share comprehensive information about tables
4. **Search Effectively**: Find relevant tables based on business terms
5. **Suggest Improvements**: Recommend better query patterns based on documentation

## Example Queries That Benefit from Wiki Metadata

- "Show me customer acquisition costs by campaign type"
- "What's the average order value for premium customers?"
- "Find products that are running low on inventory"
- "Show me sales performance by region and channel"
- "What's the customer lifetime value by tier?"

The AI agent can now understand these business concepts and generate appropriate SQL queries using the documented column names and business logic.
