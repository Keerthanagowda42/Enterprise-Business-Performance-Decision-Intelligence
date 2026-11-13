# Enterprise Business Performance & Decision Intelligence

A comprehensive enterprise analytics and decision intelligence platform evaluating sales, revenue, profit, and operational performance across 15,000 corporate purchase orders and multi-year financials.

---

## 🛠️ Tech Stack & Architecture
- **Advanced Excel**: Multi-tab dynamic financial model (`Enterprise_Performance_Model.xlsx`) featuring KPI cards, `SUMIFS`, `AVERAGEIFS`, `XLOOKUP`, and dynamic sensitivity matrices.
- **SQL**: Production-grade relational schema DDL, data cleaning ETL, and advanced analytical queries (Window functions `LAG()`, `LEAD()`, `DENSE_RANK()`, CTEs, RFM segmentation, Pareto 80/20 analysis).
- **Python**: Robust data generation (`generate_enterprise_data.py`), automated ETL and exploratory data analysis pipeline (`data_cleaning_eda.py`), and high-resolution chart rendering.
- **Power BI / BI Intelligence**: Comprehensive DAX measures library (35+ measures), Star Schema dimensional modeling, visual wireframe guides, and an interactive HTML/JS dashboard simulation (`interactive_dashboard.html`).

---

## 📁 Project Directory Structure
```
Enterprise-Business-Performance-Decision-Intelligence/
│
├── data/
│   ├── raw/                           # Raw ingested datasets (customers, products, sales_orders, operational_costs)
│   └── processed/                     # Cleaned relational SQLite DB & processed CSVs
│       ├── enterprise_data.db         # Fully indexed SQLite database (15,000+ records)
│       ├── dim_customers_clean.csv
│       ├── dim_products_clean.csv
│       ├── fact_sales_orders_clean.csv
│       └── fact_operational_costs_clean.csv
│
├── excel/
│   └── Enterprise_Performance_Model.xlsx   # Executive Excel Financial Model
│
├── sql/
│   ├── 01_schema_ddl.sql              # Star Schema DDL, constraints & indexes
│   ├── 02_data_cleaning_etl.sql       # Cleansing queries, missing value handling & normalization
│   └── 03_business_kpi_analytics.sql  # Executive KPI, YoY, Pareto, and RFM queries
│
├── python/
│   ├── generate_enterprise_data.py    # Synthetic enterprise data generator
│   ├── data_cleaning_eda.py           # Automated cleaning, EDA & chart export pipeline
│   └── build_excel_model.py           # Programmatic openpyxl financial workbook generator
│
├── power_bi/
│   ├── dax_measures.dax               # 35+ production DAX measures
│   ├── data_model_architecture.md     # Star Schema ERD & VertiPaq performance rules
│   ├── dashboard_wireframe_guide.md   # 4-page dashboard UI/UX specifications
│   └── interactive_dashboard.html     # Live, browser-runnable interactive dashboard
│
├── notebooks/
│   ├── 01_Enterprise_Performance_EDA.ipynb  # Interactive Jupyter exploratory notebook
│   └── make_p1_notebook.py            # Notebook generation script
│
└── reports/
    ├── figures/                       # High-res publication charts (PNG)
    │   ├── revenue_trends_yoy.png
    │   ├── category_profitability_matrix.png
    │   ├── regional_performance_map.png
    │   └── operational_expense_variance.png
    └── Executive_Strategic_Insights_Report.md  # C-Suite decision briefing
```

---

## 🚀 Step-by-Step Setup & Execution

### 1. Ingest Data & Initialize SQLite Relational Database:
```powershell
python python\generate_enterprise_data.py
```

### 2. Execute Data Cleaning & Statistical EDA:
```powershell
python python\data_cleaning_eda.py
```

### 3. Generate Advanced Excel Financial Workbook:
```powershell
python python\build_excel_model.py
```

### 4. Open Interactive Power BI Web Dashboard:
Simply open `power_bi/interactive_dashboard.html` in any web browser to explore dynamic filters, interactive charts, and KPI cards.

---

## 📊 Key Executive Findings
- **Total Net Recognized Revenue**: **$170.20M** (FY 2022 – FY 2024).
- **Gross Profit**: **$93.64M** (55.0% Gross Margin).
- **Operating EBITDA**: **$63.32M** (37.2% EBITDA Margin).
- **Strategic Impact**: Instituting discount thresholds (capping partner discounts at 15%) and focusing on high-margin SaaS/Cybersecurity is projected to generate **+$2.35M in incremental annual EBITDA**.

