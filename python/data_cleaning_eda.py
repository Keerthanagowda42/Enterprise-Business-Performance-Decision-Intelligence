"""
data_cleaning_eda.py
Performs Exploratory Data Analysis, Data Cleansing Validation, 
and generates executive publication-ready visualizations.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.family': 'sans-serif'})

BASE_DIR = r"C:\Users\keert\.gemini\antigravity\scratch\Enterprise-Business-Performance-Decision-Intelligence"
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "enterprise_data.db")
FIGURES_DIR = os.path.join(BASE_DIR, "reports", "figures")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("Starting Enterprise EDA & Visualization Generation...")

conn = sqlite3.connect(DB_PATH)

# Load clean tables
df_cust = pd.read_sql_query("SELECT * FROM dim_customers", conn)
df_prod = pd.read_sql_query("SELECT * FROM dim_products", conn)
df_orders = pd.read_sql_query("SELECT * FROM fact_sales_orders", conn)
df_costs = pd.read_sql_query("SELECT * FROM fact_operational_costs", conn)

# Export clean CSVs
df_cust.to_csv(os.path.join(PROCESSED_DIR, "dim_customers_clean.csv"), index=False)
df_prod.to_csv(os.path.join(PROCESSED_DIR, "dim_products_clean.csv"), index=False)
df_orders.to_csv(os.path.join(PROCESSED_DIR, "fact_sales_orders_clean.csv"), index=False)
df_costs.to_csv(os.path.join(PROCESSED_DIR, "fact_operational_costs_clean.csv"), index=False)

# Convert dates
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])
df_orders["year_month"] = df_orders["order_date"].dt.to_period("M").astype(str)
df_orders["year"] = df_orders["order_date"].dt.year
df_orders["quarter"] = df_orders["order_date"].dt.to_period("Q").astype(str)

# Join for enriched analytical dataframe
df_full = df_orders.merge(df_cust, on="customer_id", how="left").merge(df_prod, on="product_id", how="left")

# 1. SUMMARY BUSINESS METRICS
total_revenue = df_full["net_revenue"].sum()
total_cogs = df_full["cogs"].sum()
total_gross_profit = df_full["gross_profit"].sum()
overall_margin_pct = (total_gross_profit / total_revenue) * 100
total_opex = df_costs["actual_cost"].sum()
operating_income = total_gross_profit - total_opex
operating_margin_pct = (operating_income / total_revenue) * 100

print("="*60)
print("ENTERPRISE BUSINESS PERFORMANCE METRICS (2022 - 2024)")
print(f"Total Net Revenue:        ${total_revenue:,.2f}")
print(f"Cost of Goods Sold (COGS): ${total_cogs:,.2f}")
print(f"Gross Profit:             ${total_gross_profit:,.2f} ({overall_margin_pct:.1f}% Margin)")
print(f"Operating Expenses:       ${total_opex:,.2f}")
print(f"Operating Income (EBITDA):${operating_income:,.2f} ({operating_margin_pct:.1f}% Margin)")
print("="*60)

# -------------------------------------------------------------
# CHART 1: MONTHLY NET REVENUE & GROSS PROFIT RUN-RATE (YoY)
# -------------------------------------------------------------
monthly_agg = df_full.groupby("year_month").agg(
    net_revenue=("net_revenue", "sum"),
    gross_profit=("gross_profit", "sum")
).reset_index()

plt.figure(figsize=(14, 6))
plt.plot(monthly_agg["year_month"], monthly_agg["net_revenue"] / 1e6, marker='o', linewidth=2.5, color='#1f77b4', label='Net Revenue ($M)')
plt.plot(monthly_agg["year_month"], monthly_agg["gross_profit"] / 1e6, marker='s', linewidth=2, color='#2ca02c', label='Gross Profit ($M)')
plt.fill_between(monthly_agg["year_month"], monthly_agg["gross_profit"] / 1e6, alpha=0.15, color='#2ca02c')

plt.title("Enterprise Revenue & Profitability Trajectory (2022 - 2024)", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("Month", fontsize=12, fontweight='semibold')
plt.ylabel("USD in Millions ($M)", fontsize=12, fontweight='semibold')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.yticks(fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(frameon=True, facecolor='white', loc='upper left', fontsize=11)
plt.tight_layout()
chart1_path = os.path.join(FIGURES_DIR, "revenue_trends_yoy.png")
plt.savefig(chart1_path, dpi=300)
plt.close()
print(f"Saved: {chart1_path}")

# -------------------------------------------------------------
# CHART 2: CATEGORY PROFITABILITY & MARGIN MATRIX
# -------------------------------------------------------------
cat_col = "category" if "category" in df_full.columns else "category_x"
cat_agg = df_full.groupby(cat_col).agg(
    net_revenue=("net_revenue", "sum"),
    cogs=("cogs", "sum"),
    gross_profit=("gross_profit", "sum")
).reset_index()
cat_agg["margin_pct"] = (cat_agg["gross_profit"] / cat_agg["net_revenue"]) * 100
cat_agg = cat_agg.sort_values("net_revenue", ascending=False)

fig, ax1 = plt.subplots(figsize=(12, 6))
color = '#0f4c81'
bars = ax1.bar(cat_agg[cat_col], cat_agg["net_revenue"] / 1e6, color=color, alpha=0.85, width=0.55, label='Net Revenue ($M)')
ax1.set_xlabel('Product Category', fontsize=12, fontweight='bold')
ax1.set_ylabel('Net Revenue ($M)', color=color, fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=color)
plt.xticks(rotation=15, ha='right', fontsize=10)

# Secondary axis for Margin %
ax2 = ax1.twinx()
color = '#e65100'
line = ax2.plot(cat_agg[cat_col], cat_agg["margin_pct"], color=color, marker='D', linewidth=3, markersize=8, label='Gross Margin %')
ax2.set_ylabel('Gross Margin (%)', color=color, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 100)

for p, val in zip(bars, cat_agg["net_revenue"] / 1e6):
    ax1.annotate(f"${val:.1f}M", (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                 ha='center', va='center', color='white', fontweight='bold', fontsize=10)

for x, val in zip(range(len(cat_agg)), cat_agg["margin_pct"]):
    ax2.annotate(f"{val:.1f}%", (x, val + 2.5),
                 ha='center', va='bottom', color=color, fontweight='bold', fontsize=10)

plt.title("Revenue Contribution & Margin Efficiency by Product Category", fontsize=15, fontweight='bold', pad=15)
fig.tight_layout()
chart2_path = os.path.join(FIGURES_DIR, "category_profitability_matrix.png")
plt.savefig(chart2_path, dpi=300)
plt.close()
print(f"Saved: {chart2_path}")

# -------------------------------------------------------------
# CHART 3: REGIONAL & CUSTOMER SEGMENT PERFORMANCE HEATMAP
# -------------------------------------------------------------
pivot_region_seg = df_full.pivot_table(
    index="region",
    columns="segment",
    values="net_revenue",
    aggfunc="sum"
) / 1e6

plt.figure(figsize=(10, 6))
sns.heatmap(pivot_region_seg, annot=True, fmt=".2f", cmap="YlGnBu", cbar_kws={'label': 'Revenue ($M)'}, annot_kws={"fontsize": 11, "fontweight": "bold"})
plt.title("Enterprise Revenue by Region and Customer Segment ($ Millions)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Customer Segment", fontsize=11, fontweight='semibold')
plt.ylabel("Geographic Region", fontsize=11, fontweight='semibold')
plt.tight_layout()
chart3_path = os.path.join(FIGURES_DIR, "regional_performance_map.png")
plt.savefig(chart3_path, dpi=300)
plt.close()
print(f"Saved: {chart3_path}")

# -------------------------------------------------------------
# CHART 4: OPERATIONAL EXPENSE VARIANCE BY DEPARTMENT
# -------------------------------------------------------------
dept_costs = df_costs.groupby("department").agg(
    total_budget=("budgeted_cost", "sum"),
    total_actual=("actual_cost", "sum"),
    total_variance=("variance", "sum")
).reset_index()

dept_costs["variance_k"] = dept_costs["total_variance"] / 1000

plt.figure(figsize=(11, 5))
colors = ['#d9534f' if v > 0 else '#5cb85c' for v in dept_costs["variance_k"]]
bars = plt.barh(dept_costs["department"], dept_costs["variance_k"], color=colors, height=0.6)
plt.axvline(0, color='black', linewidth=1, linestyle='--')
plt.title("Operational Cost Variance: Budget vs Actual by Department ($k)", fontsize=14, fontweight='bold', pad=12)
plt.xlabel("Net Budget Variance ($k) [Red = Over Budget, Green = Under Budget]", fontsize=11, fontweight='semibold')
plt.ylabel("Department", fontsize=11, fontweight='semibold')

for bar in bars:
    w = bar.get_width()
    ha = 'left' if w >= 0 else 'right'
    offset = 5 if w >= 0 else -5
    plt.annotate(f"${w:+.1f}k", (w + offset, bar.get_y() + bar.get_height() / 2),
                 va='center', ha=ha, fontsize=10, fontweight='bold')

plt.tight_layout()
chart4_path = os.path.join(FIGURES_DIR, "operational_expense_variance.png")
plt.savefig(chart4_path, dpi=300)
plt.close()
print(f"Saved: {chart4_path}")

conn.close()
print("All EDA charts generated successfully!")
