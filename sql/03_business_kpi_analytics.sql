-- =====================================================================
-- Project 1: Enterprise Business Performance & Decision Intelligence
-- Script 03: Advanced Analytical SQL Queries & Business KPI Calculations
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. EXECUTIVE REVENUE & PROFITABILITY RUN-RATE (Monthly & YoY Growth)
-- Uses Window Functions LAG() to compute MoM & YoY revenue trends
-- ---------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT 
        STRFTIME('%Y-%m', order_date) AS year_month,
        STRFTIME('%Y', order_date) AS order_year,
        STRFTIME('%m', order_date) AS order_month,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(net_revenue) AS monthly_net_revenue,
        SUM(cogs) AS monthly_cogs,
        SUM(gross_profit) AS monthly_gross_profit,
        ROUND((SUM(gross_profit) / NULLIF(SUM(net_revenue), 0)) * 100, 2) AS gross_margin_pct
    FROM fact_sales_orders
    GROUP BY STRFTIME('%Y-%m', order_date)
),
mom_trends AS (
    SELECT 
        year_month,
        total_orders,
        active_customers,
        monthly_net_revenue,
        monthly_gross_profit,
        gross_margin_pct,
        LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        ROUND(((monthly_net_revenue - LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month)) / 
               NULLIF(LAG(monthly_net_revenue, 1) OVER (ORDER BY year_month), 0)) * 100, 2) AS mom_growth_pct,
        LAG(monthly_net_revenue, 12) OVER (ORDER BY year_month) AS prev_year_revenue,
        ROUND(((monthly_net_revenue - LAG(monthly_net_revenue, 12) OVER (ORDER BY year_month)) / 
               NULLIF(LAG(monthly_net_revenue, 12) OVER (ORDER BY year_month), 0)) * 100, 2) AS yoy_growth_pct
    FROM monthly_metrics
)
SELECT * FROM mom_trends
ORDER BY year_month DESC;


-- ---------------------------------------------------------------------
-- 2. PRODUCT CATEGORY & SUBCATEGORY PROFITABILITY RANKING
-- Identifies top margin drivers vs volume drivers using DENSE_RANK()
-- ---------------------------------------------------------------------
WITH category_performance AS (
    SELECT 
        p.category,
        p.subcategory,
        COUNT(f.order_id) AS total_orders,
        SUM(f.quantity) AS total_units_sold,
        ROUND(SUM(f.net_revenue), 2) AS total_net_revenue,
        ROUND(SUM(f.cogs), 2) AS total_cogs,
        ROUND(SUM(f.gross_profit), 2) AS total_gross_profit,
        ROUND((SUM(f.gross_profit) / NULLIF(SUM(f.net_revenue), 0)) * 100, 2) AS category_margin_pct,
        ROUND(AVG(f.discount_pct) * 100, 2) AS avg_discount_pct
    FROM fact_sales_orders f
    JOIN dim_products p ON f.product_id = p.product_id
    GROUP BY p.category, p.subcategory
)
SELECT 
    category,
    subcategory,
    total_orders,
    total_units_sold,
    total_net_revenue,
    total_gross_profit,
    category_margin_pct,
    avg_discount_pct,
    DENSE_RANK() OVER (ORDER BY total_net_revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (ORDER BY total_gross_profit DESC) AS profit_rank,
    DENSE_RANK() OVER (ORDER BY category_margin_pct DESC) AS margin_efficiency_rank
FROM category_performance
ORDER BY total_net_revenue DESC;


-- ---------------------------------------------------------------------
-- 3. PARETO 80/20 ANALYSIS (Product Revenue Concentration)
-- Uses Cumulative Running Totals to determine product concentration
-- ---------------------------------------------------------------------
WITH product_totals AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(f.net_revenue) AS product_revenue
    FROM fact_sales_orders f
    JOIN dim_products p ON f.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
),
product_ranking AS (
    SELECT 
        product_id,
        product_name,
        category,
        product_revenue,
        SUM(product_revenue) OVER () AS total_enterprise_revenue,
        SUM(product_revenue) OVER (ORDER BY product_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_cumulative_revenue,
        ROW_NUMBER() OVER (ORDER BY product_revenue DESC) AS product_rank,
        COUNT(*) OVER () AS total_products_count
    FROM product_totals
)
SELECT 
    product_id,
    product_name,
    category,
    ROUND(product_revenue, 2) AS product_revenue,
    ROUND(running_cumulative_revenue, 2) AS running_cumulative_revenue,
    ROUND((running_cumulative_revenue / total_enterprise_revenue) * 100, 2) AS cumulative_revenue_pct,
    ROUND((CAST(product_rank AS FLOAT) / total_products_count) * 100, 2) AS cumulative_products_pct,
    CASE 
        WHEN (running_cumulative_revenue / total_enterprise_revenue) <= 0.80 THEN 'Top 80% Core Revenue Driver (Pareto Tier A)'
        WHEN (running_cumulative_revenue / total_enterprise_revenue) <= 0.95 THEN 'Next 15% Sustaining Driver (Pareto Tier B)'
        ELSE 'Long-Tail Low Impact (Pareto Tier C)'
    END AS pareto_classification
FROM product_ranking
ORDER BY product_rank;


-- ---------------------------------------------------------------------
-- 4. CUSTOMER RFM (Recency, Frequency, Monetary) SEGMENTATION
-- Segments customer accounts into Champions, Loyal, At Risk, and Hibernating
-- ---------------------------------------------------------------------
WITH rfm_base AS (
    SELECT 
        c.customer_id,
        c.company_name,
        c.segment,
        c.region,
        c.industry,
        CAST(JULIANDAY('2024-12-31') - JULIANDAY(MAX(f.order_date)) AS INT) AS recency_days,
        COUNT(DISTINCT f.order_id) AS order_frequency,
        ROUND(SUM(f.net_revenue), 2) AS total_monetary_spend,
        ROUND(AVG(f.net_revenue), 2) AS avg_order_value,
        ROUND(SUM(f.gross_profit), 2) AS total_profit_contribution
    FROM dim_customers c
    JOIN fact_sales_orders f ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.company_name, c.segment, c.region, c.industry
),
rfm_scores AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score, -- Lower days = higher score
        NTILE(5) OVER (ORDER BY order_frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY total_monetary_spend ASC) AS m_score
    FROM rfm_base
)
SELECT 
    customer_id,
    company_name,
    segment,
    region,
    industry,
    recency_days,
    order_frequency,
    total_monetary_spend,
    total_profit_contribution,
    r_score,
    f_score,
    m_score,
    (r_score + f_score + m_score) AS composite_rfm_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Platinum Enterprise Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'High-Value Loyal Accounts'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At-Risk High Spenders (Immediate Retention Action)'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Recent Onboarded Accounts'
        ELSE 'Hibernating / Low Engagement'
    END AS strategic_customer_segment
FROM rfm_scores
ORDER BY total_monetary_spend DESC;


-- ---------------------------------------------------------------------
-- 5. OPERATIONAL EXPENSE & BUDGET VARIANCE BY DEPARTMENT
-- Evaluates budget discipline and cost overruns
-- ---------------------------------------------------------------------
SELECT 
    department,
    STRFTIME('%Y', month_date) AS expense_year,
    ROUND(SUM(budgeted_cost), 2) AS annual_budget,
    ROUND(SUM(actual_cost), 2) AS annual_actual_spend,
    ROUND(SUM(variance), 2) AS net_variance,
    ROUND((SUM(variance) / NULLIF(SUM(budgeted_cost), 0)) * 100, 2) AS variance_pct,
    SUM(CASE WHEN is_over_budget = 1 THEN 1 ELSE 0 END) AS over_budget_months_count,
    COUNT(*) AS total_months
FROM fact_operational_costs
GROUP BY department, STRFTIME('%Y', month_date)
ORDER BY expense_year DESC, net_variance DESC;


-- ---------------------------------------------------------------------
-- 6. SUPPLY CHAIN & FULFILLMENT EFFICIENCY
-- Measures lead times, on-time delivery rates across regions & modes
-- ---------------------------------------------------------------------
SELECT 
    c.region,
    f.fulfillment_mode,
    COUNT(f.order_id) AS total_shipments,
    ROUND(AVG(f.lead_time_days), 2) AS avg_lead_time_days,
    ROUND(
        (SUM(CASE WHEN f.delivery_status = 'Delivered On-Time' THEN 1 ELSE 0 END) * 100.0) / 
        COUNT(f.order_id), 2
    ) AS on_time_delivery_rate_pct,
    ROUND(
        (SUM(CASE WHEN f.delivery_status = 'Delivered Delayed' THEN 1 ELSE 0 END) * 100.0) / 
        COUNT(f.order_id), 2
    ) AS delayed_delivery_rate_pct,
    ROUND(
        (SUM(CASE WHEN f.delivery_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0) / 
        COUNT(f.order_id), 2
    ) AS cancellation_rate_pct
FROM fact_sales_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.region, f.fulfillment_mode
ORDER BY c.region, total_shipments DESC;

