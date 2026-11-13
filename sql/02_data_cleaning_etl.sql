-- =====================================================================
-- Project 1: Enterprise Business Performance & Decision Intelligence
-- Script 02: Data Cleaning, Transformation & ETL Pipeline
-- Database Target: SQLite
-- =====================================================================

-- Step 1: Clean and Populate Dim_Customers
INSERT OR REPLACE INTO dim_customers (
    customer_id, company_name, segment, industry, region, credit_tier, acquisition_date, account_manager
)
SELECT 
    TRIM(customer_id) AS customer_id,
    TRIM(company_name) AS company_name,
    COALESCE(segment, 'Mid-Market') AS segment,
    COALESCE(industry, 'General Business') AS industry,
    COALESCE(region, 'North America') AS region,
    COALESCE(credit_tier, 'Tier 3 (A)') AS credit_tier,
    acquisition_date,
    COALESCE(account_manager, 'Unassigned') AS account_manager
FROM raw_customers
WHERE customer_id IS NOT NULL;

-- Step 2: Clean and Populate Dim_Products
INSERT OR REPLACE INTO dim_products (
    product_id, product_name, category, subcategory, tier, unit_cost, unit_price, is_active
)
SELECT 
    TRIM(product_id) AS product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    TRIM(subcategory) AS subcategory,
    TRIM(tier) AS tier,
    ABS(unit_cost) AS unit_cost,
    ABS(unit_price) AS unit_price,
    COALESCE(is_active, 1) AS is_active
FROM raw_products
WHERE product_id IS NOT NULL AND unit_price > 0;

-- Step 3: Clean and Populate Fact_Sales_Orders
-- Cleans negative revenue anomalies and null delivery statuses
INSERT OR REPLACE INTO fact_sales_orders (
    order_id, customer_id, product_id, order_date, ship_date, sales_channel, fulfillment_mode,
    lead_time_days, quantity, unit_price, unit_cost, gross_revenue, discount_pct,
    discount_amount, net_revenue, cogs, gross_profit, gross_margin_pct, delivery_status
)
SELECT 
    TRIM(order_id) AS order_id,
    TRIM(customer_id) AS customer_id,
    TRIM(product_id) AS product_id,
    order_date,
    ship_date,
    COALESCE(sales_channel, 'Direct Sales') AS sales_channel,
    COALESCE(fulfillment_mode, 'Standard Freight') AS fulfillment_mode,
    MAX(0, lead_time_days) AS lead_time_days,
    MAX(1, quantity) AS quantity,
    ABS(unit_price) AS unit_price,
    ABS(unit_cost) AS unit_cost,
    ROUND(ABS(unit_price) * MAX(1, quantity), 2) AS gross_revenue,
    CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END AS discount_pct,
    ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) * 
          (CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END), 2) AS discount_amount,
    -- Recalculate net revenue properly handling inverted signs in raw data
    ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) - 
          ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) * 
          (CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END), 2), 2) AS net_revenue,
    ROUND(ABS(unit_cost) * MAX(1, quantity), 2) AS cogs,
    -- Recalculate gross profit
    ROUND(
        ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) - 
              ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) * 
              (CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END), 2), 2)
        - ROUND(ABS(unit_cost) * MAX(1, quantity), 2), 2
    ) AS gross_profit,
    -- Recalculate gross margin pct
    ROUND(
        (
            ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) - 
                  ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) * 
                  (CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END), 2), 2)
            - ROUND(ABS(unit_cost) * MAX(1, quantity), 2)
        ) / 
        NULLIF(
            ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) - 
                  ROUND(ROUND(ABS(unit_price) * MAX(1, quantity), 2) * 
                  (CASE WHEN discount_pct < 0 OR discount_pct > 1 THEN 0.0 ELSE discount_pct END), 2), 2), 0
        ) * 100, 2
    ) AS gross_margin_pct,
    COALESCE(delivery_status, 'Delivered On-Time') AS delivery_status
FROM raw_orders
WHERE order_id IS NOT NULL;

-- Step 4: Clean and Populate Fact_Operational_Costs
INSERT OR REPLACE INTO fact_operational_costs (
    expense_id, month_date, department, budgeted_cost, actual_cost, variance, variance_pct, is_over_budget
)
SELECT 
    TRIM(expense_id) AS expense_id,
    month_date,
    TRIM(department) AS department,
    ROUND(budgeted_cost, 2) AS budgeted_cost,
    ROUND(actual_cost, 2) AS actual_cost,
    ROUND(actual_cost - budgeted_cost, 2) AS variance,
    ROUND(((actual_cost - budgeted_cost) / NULLIF(budgeted_cost, 0)) * 100, 2) AS variance_pct,
    CASE WHEN actual_cost > budgeted_cost THEN 1 ELSE 0 END AS is_over_budget
FROM raw_operational_costs
WHERE expense_id IS NOT NULL;

