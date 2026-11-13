"""
generate_enterprise_data.py
Generates realistic, rich enterprise datasets for Enterprise Business Performance & Decision Intelligence.
Creates raw CSV files and populates an SQLite database.
"""

import os
import random
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = r"C:\Users\keert\.gemini\antigravity\scratch\Enterprise-Business-Performance-Decision-Intelligence"
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

print("Starting Enterprise Data Generation...")

# 1. GENERATE CUSTOMERS (1,000 enterprise accounts)
regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
region_weights = [0.45, 0.30, 0.18, 0.07]

segments = ["Enterprise", "Mid-Market", "Small Business"]
segment_weights = [0.25, 0.45, 0.30]

industries = ["Technology", "Financial Services", "Healthcare", "Manufacturing", "Retail & Consumer"]
industry_weights = [0.30, 0.25, 0.20, 0.15, 0.10]

credit_tiers = ["Tier 1 (AAA)", "Tier 2 (AA)", "Tier 3 (A)", "Tier 4 (BBB)"]
credit_weights = [0.40, 0.35, 0.18, 0.07]

customer_ids = [f"CUST-{1000 + i}" for i in range(1000)]
start_acq_date = datetime(2020, 1, 1)

customers_data = []
for cid in customer_ids:
    reg = np.random.choice(regions, p=region_weights)
    seg = np.random.choice(segments, p=segment_weights)
    ind = np.random.choice(industries, p=industry_weights)
    c_tier = np.random.choice(credit_tiers, p=credit_weights)
    acq_days = np.random.randint(0, 1400)
    acq_date = (start_acq_date + timedelta(days=int(acq_days))).strftime("%Y-%m-%d")
    
    customers_data.append({
        "customer_id": cid,
        "company_name": f"{ind[:4].upper()}-{cid[-4:]} Corp",
        "segment": seg,
        "industry": ind,
        "region": reg,
        "credit_tier": c_tier,
        "acquisition_date": acq_date,
        "account_manager": f"Rep-{np.random.randint(1, 25):02d}"
    })

df_customers = pd.DataFrame(customers_data)
df_customers.to_csv(os.path.join(RAW_DATA_DIR, "customers.csv"), index=False)
print(f"Generated {len(df_customers)} customers.")

# 2. GENERATE PRODUCTS (60 enterprise products)
categories_subcategories = {
    "Cloud Infrastructure": ["Compute Nodes", "Storage Solutions", "Networking", "Managed Kubernetes"],
    "Enterprise Software": ["ERP Modules", "CRM Suite", "Analytics Platform", "Security Information"],
    "Cybersecurity": ["Endpoint Protection", "Zero Trust Gateway", "SIEM & SOC", "Identity Governance"],
    "Professional Services": ["Implementation", "Custom Engineering", "Architecture Advisory", "24/7 Managed Ops"],
    "Hardware & Appliances": ["Data Center Servers", "Edge Gateway Devices", "Backup Appliances"]
}

products_data = []
p_counter = 100
for cat, subcats in categories_subcategories.items():
    for subcat in subcats:
        num_variants = np.random.randint(2, 5)
        for v in range(num_variants):
            pid = f"PROD-{p_counter}"
            p_counter += 1
            
            # Base cost and margin based on category
            if cat == "Cloud Infrastructure":
                base_cost = np.random.uniform(500, 4000)
                margin_rate = np.random.uniform(0.40, 0.65)
            elif cat == "Enterprise Software":
                base_cost = np.random.uniform(200, 2500)
                margin_rate = np.random.uniform(0.70, 0.88) # High software margin
            elif cat == "Cybersecurity":
                base_cost = np.random.uniform(400, 3000)
                margin_rate = np.random.uniform(0.65, 0.82)
            elif cat == "Professional Services":
                base_cost = np.random.uniform(150, 1800)
                margin_rate = np.random.uniform(0.35, 0.55) # Services margin
            else: # Hardware
                base_cost = np.random.uniform(1200, 8000)
                margin_rate = np.random.uniform(0.20, 0.38) # Lower hardware margin
                
            unit_cost = round(base_cost, 2)
            unit_price = round(unit_cost / (1.0 - margin_rate), 2)
            
            tier = np.random.choice(["Core", "Premium", "Enterprise Advantage"], p=[0.5, 0.35, 0.15])
            
            products_data.append({
                "product_id": pid,
                "product_name": f"{subcat} {tier} (v{v+1}.0)",
                "category": cat,
                "subcategory": subcat,
                "tier": tier,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "is_active": True
            })

df_products = pd.DataFrame(products_data)
df_products.to_csv(os.path.join(RAW_DATA_DIR, "products.csv"), index=False)
print(f"Generated {len(df_products)} products.")

# 3. GENERATE SALES ORDERS (15,000 transaction orders 2022-2024)
start_order_date = datetime(2022, 1, 1)
end_order_date = datetime(2024, 12, 31)
total_days = (end_order_date - start_order_date).days

sales_channels = ["Direct Sales", "Partner / Reseller", "Digital Portal", "Inside Sales"]
channel_weights = [0.45, 0.30, 0.15, 0.10]

fulfillment_modes = ["Express Delivery", "Standard Freight", "Digital License Dispatch", "On-Prem Deployment"]

orders_data = []
product_dict = df_products.set_index("product_id").to_dict(orient="index")
customer_ids_list = df_customers["customer_id"].tolist()

# Add deliberate seasonal & trend patterns
for i in range(1, 15001):
    oid = f"ORD-{20220000 + i}"
    cid = np.random.choice(customer_ids_list)
    pid = np.random.choice(df_products["product_id"])
    prod_info = product_dict[pid]
    
    # Days offset with slight upward growth trend over 3 years
    # Skew slightly towards Q3/Q4 enterprise budget spend
    day_offset = int(np.random.beta(1.4, 1.1) * total_days)
    order_dt = start_order_date + timedelta(days=day_offset)
    
    # Month seasonality: Q4 bump (Oct, Nov, Dec)
    if order_dt.month in [11, 12] and np.random.random() < 0.25:
        # Extra boost
        quantity = np.random.choice([1, 2, 3, 5, 8, 12, 20], p=[0.30, 0.25, 0.18, 0.12, 0.08, 0.05, 0.02])
    else:
        quantity = np.random.choice([1, 2, 3, 5, 8, 12, 20], p=[0.40, 0.28, 0.15, 0.09, 0.05, 0.02, 0.01])
        
    unit_p = prod_info["unit_price"]
    unit_c = prod_info["unit_cost"]
    
    # Discount rate varies with volume and channel
    channel = np.random.choice(sales_channels, p=channel_weights)
    if channel == "Direct Sales" and quantity >= 5:
        discount = np.random.choice([0.10, 0.15, 0.20, 0.25], p=[0.4, 0.3, 0.2, 0.1])
    elif channel == "Partner / Reseller":
        discount = np.random.choice([0.15, 0.20, 0.25], p=[0.5, 0.35, 0.15])
    else:
        discount = np.random.choice([0.0, 0.05, 0.10], p=[0.6, 0.3, 0.1])
        
    gross_revenue = round(unit_p * quantity, 2)
    discount_amount = round(gross_revenue * discount, 2)
    net_revenue = round(gross_revenue - discount_amount, 2)
    total_cogs = round(unit_c * quantity, 2)
    gross_profit = round(net_revenue - total_cogs, 2)
    gross_margin_pct = round((gross_profit / net_revenue) * 100, 2) if net_revenue > 0 else 0.0
    
    # Fulfillment
    lead_days = int(np.random.gamma(shape=3.0, scale=1.5)) + 1
    ship_dt = order_dt + timedelta(days=lead_days)
    delivery_status = np.random.choice(["Delivered On-Time", "Delivered Delayed", "Shipped in Transit", "Cancelled"], 
                                      p=[0.88, 0.08, 0.03, 0.01])
    
    # Introduce ~0.5% dirty data intentionally to test cleaning & validation pipeline
    if i % 200 == 0:
        net_revenue = -1 * abs(net_revenue) # Anomaly to clean
    if i % 350 == 0:
        delivery_status = None # Missing value
        
    orders_data.append({
        "order_id": oid,
        "customer_id": cid,
        "product_id": pid,
        "order_date": order_dt.strftime("%Y-%m-%d"),
        "ship_date": ship_dt.strftime("%Y-%m-%d"),
        "sales_channel": channel,
        "fulfillment_mode": np.random.choice(fulfillment_modes),
        "lead_time_days": lead_days,
        "quantity": quantity,
        "unit_price": unit_p,
        "unit_cost": unit_c,
        "gross_revenue": gross_revenue,
        "discount_pct": discount,
        "discount_amount": discount_amount,
        "net_revenue": net_revenue,
        "cogs": total_cogs,
        "gross_profit": gross_profit,
        "gross_margin_pct": gross_margin_pct,
        "delivery_status": delivery_status
    })

df_orders = pd.DataFrame(orders_data)
df_orders.to_csv(os.path.join(RAW_DATA_DIR, "sales_orders.csv"), index=False)
print(f"Generated {len(df_orders)} sales orders.")

# 4. GENERATE OPERATIONAL COSTS (36 months across 5 departments)
months = pd.date_range(start="2022-01-01", end="2024-12-01", freq="MS")
departments = [
    {"name": "Research & Development", "base_budget": 180000, "variance_std": 12000},
    {"name": "Sales & Marketing", "base_budget": 240000, "variance_std": 20000},
    {"name": "General & Administrative", "base_budget": 110000, "variance_std": 8000},
    {"name": "Customer Support & Success", "base_budget": 95000, "variance_std": 6000},
    {"name": "Cloud Operations & IT", "base_budget": 150000, "variance_std": 15000}
]

cost_records = []
cost_id = 1
for m in months:
    m_str = m.strftime("%Y-%m-%d")
    year_mult = 1.0 + (m.year - 2022) * 0.08 # 8% annual inflation/growth
    for d in departments:
        cid = f"EXP-{cost_id:04d}"
        cost_id += 1
        budget = round(d["base_budget"] * year_mult, 2)
        # Random variance
        actual = round(budget + np.random.normal(0, d["variance_std"]), 2)
        variance = round(actual - budget, 2)
        variance_pct = round((variance / budget) * 100, 2)
        
        cost_records.append({
            "expense_id": cid,
            "month_date": m_str,
            "department": d["name"],
            "budgeted_cost": budget,
            "actual_cost": actual,
            "variance": variance,
            "variance_pct": variance_pct,
            "is_over_budget": actual > budget
        })

df_costs = pd.DataFrame(cost_records)
df_costs.to_csv(os.path.join(RAW_DATA_DIR, "operational_costs.csv"), index=False)
print(f"Generated {len(df_costs)} operational cost records.")

# 5. LOAD INTO SQLITE DATABASE
db_path = os.path.join(PROCESSED_DATA_DIR, "enterprise_data.db")
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_customers.to_sql("raw_customers", conn, if_exists="replace", index=False)
df_products.to_sql("raw_products", conn, if_exists="replace", index=False)
df_orders.to_sql("raw_orders", conn, if_exists="replace", index=False)
df_costs.to_sql("raw_operational_costs", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

print(f"Enterprise Data successfully generated and saved to {RAW_DATA_DIR} and {db_path}!")

