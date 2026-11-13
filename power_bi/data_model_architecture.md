# Enterprise Business Performance Data Model Architecture

## 1. Architectural Overview & Star Schema
The enterprise decision intelligence system is built upon a Kimball-style dimensional star schema optimized for in-memory Power BI tabular engine (VertiPaq) performance, bidirectional filter safety, and sub-second query latency.

```mermaid
erDiagram
    dim_date ||--o{ fact_sales_orders : "order_date"
    dim_date ||--o{ fact_operational_costs : "month_date"
    dim_customers ||--o{ fact_sales_orders : "customer_id"
    dim_products ||--o{ fact_sales_orders : "product_id"

    dim_date {
        date date_key PK
        int year
        string quarter
        string month_name
        int month_number
        int day_of_month
        string fiscal_year
        boolean is_weekend
    }

    dim_customers {
        string customer_id PK
        string company_name
        string segment
        string industry
        string region
        string credit_tier
        date acquisition_date
        string account_manager
    }

    dim_products {
        string product_id PK
        string product_name
        string category
        string subcategory
        string tier
        decimal unit_cost
        decimal unit_price
        boolean is_active
    }

    fact_sales_orders {
        string order_id PK
        string customer_id FK
        string product_id FK
        date order_date FK
        date ship_date
        string sales_channel
        string fulfillment_mode
        int lead_time_days
        int quantity
        decimal unit_price
        decimal unit_cost
        decimal gross_revenue
        decimal discount_pct
        decimal discount_amount
        decimal net_revenue
        decimal cogs
        decimal gross_profit
        decimal gross_margin_pct
        string delivery_status
    }

    fact_operational_costs {
        string expense_id PK
        date month_date FK
        string department
        decimal budgeted_cost
        decimal actual_cost
        decimal variance
        decimal variance_pct
        boolean is_over_budget
    }
```

## 2. Table Cardinalities & Relationship Rules
1. **`dim_customers (1)` to `fact_sales_orders (*)`**:
   - Primary Key: `customer_id` -> Foreign Key: `customer_id`
   - Cross-filter direction: **Single** (Dimension filters Fact table)
   - Cardinality: **1 to Many**

2. **`dim_products (1)` to `fact_sales_orders (*)`**:
   - Primary Key: `product_id` -> Foreign Key: `product_id`
   - Cross-filter direction: **Single**
   - Cardinality: **1 to Many**

3. **`dim_date (1)` to `fact_sales_orders (*)`**:
   - Primary Key: `date_key` -> Foreign Key: `order_date` (Active)
   - Inactive Secondary Relationship: `date_key` -> `ship_date` (activated via `USERELATIONSHIP()` in DAX for fulfillment analysis)
   - Cardinality: **1 to Many**

4. **`dim_date (1)` to `fact_operational_costs (*)`**:
   - Primary Key: `date_key` -> Foreign Key: `month_date`
   - Aggregated at the monthly grain (1st of each month).

## 3. VertiPaq Storage Engine Optimizations
- **Data Types**: All financial columns are set to Fixed Decimal Number (`Currency`) to eliminate floating-point drift and maximize VertiPaq run-length encoding (RLE).
- **Date Dimension**: Pre-computed surrogate date integer keys `YYYYMMDD` for ultra-fast joins.
- **Bi-directional Filtering Disabled**: Cross-filtering is strictly single-directional to prevent circular relationship ambiguities and high memory consumption.

