-- =====================================================================
-- Project 1: Enterprise Business Performance & Decision Intelligence
-- Script 01: Relational Schema DDL & Constraints
-- Database Target: SQLite / PostgreSQL / SQL Server Compatible
-- =====================================================================

-- 1. Dim_Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(30) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL CHECK (segment IN ('Enterprise', 'Mid-Market', 'Small Business')),
    industry VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL CHECK (region IN ('North America', 'Europe', 'Asia-Pacific', 'Latin America')),
    credit_tier VARCHAR(50) NOT NULL,
    acquisition_date DATE NOT NULL,
    account_manager VARCHAR(50) NOT NULL
);

-- Index for customer region and segment slicing
CREATE INDEX IF NOT EXISTS idx_customers_region ON dim_customers(region);
CREATE INDEX IF NOT EXISTS idx_customers_segment ON dim_customers(segment);
CREATE INDEX IF NOT EXISTS idx_customers_industry ON dim_customers(industry);

-- 2. Dim_Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    subcategory VARCHAR(80) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(12, 2) NOT NULL CHECK (unit_cost >= 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    is_active BOOLEAN DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_products_category ON dim_products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON dim_products(subcategory);

-- 3. Fact_Sales_Orders
CREATE TABLE IF NOT EXISTS fact_sales_orders (
    order_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    sales_channel VARCHAR(50) NOT NULL,
    fulfillment_mode VARCHAR(50) NOT NULL,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL,
    unit_cost DECIMAL(12, 2) NOT NULL,
    gross_revenue DECIMAL(14, 2) NOT NULL,
    discount_pct DECIMAL(5, 4) NOT NULL CHECK (discount_pct >= 0 AND discount_pct <= 1),
    discount_amount DECIMAL(14, 2) NOT NULL,
    net_revenue DECIMAL(14, 2) NOT NULL,
    cogs DECIMAL(14, 2) NOT NULL,
    gross_profit DECIMAL(14, 2) NOT NULL,
    gross_margin_pct DECIMAL(7, 2) NOT NULL,
    delivery_status VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_order_date ON fact_sales_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON fact_sales_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON fact_sales_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_channel ON fact_sales_orders(sales_channel);

-- 4. Fact_Operational_Costs
CREATE TABLE IF NOT EXISTS fact_operational_costs (
    expense_id VARCHAR(30) PRIMARY KEY,
    month_date DATE NOT NULL,
    department VARCHAR(80) NOT NULL,
    budgeted_cost DECIMAL(14, 2) NOT NULL,
    actual_cost DECIMAL(14, 2) NOT NULL,
    variance DECIMAL(14, 2) NOT NULL,
    variance_pct DECIMAL(7, 2) NOT NULL,
    is_over_budget BOOLEAN NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_costs_month_dept ON fact_operational_costs(month_date, department);

