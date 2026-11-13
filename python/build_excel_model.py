"""
build_excel_model.py
Generates an advanced, multi-tab Excel financial model using openpyxl:
- Executive Summary with KPI metric cards & dynamic formulas
- Category & Subcategory Performance with SUMIFS / AVERAGEIFS
- Regional Analysis with Market Share formulas
- Dynamic What-If Sensitivity Modeler (Price vs Discount impact on EBITDA)
- Transactions Data Sheet
- Data Dictionary
"""

import os
import sqlite3
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = r"C:\Users\keert\.gemini\antigravity\scratch\Enterprise-Business-Performance-Decision-Intelligence"
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "enterprise_data.db")
EXCEL_PATH = os.path.join(BASE_DIR, "excel", "Enterprise_Performance_Model.xlsx")

print("Building Advanced Excel Performance Model...")

conn = sqlite3.connect(DB_PATH)
df_orders = pd.read_sql_query("""
    SELECT 
        o.order_id, o.order_date, c.region, c.segment, c.industry,
        p.category, p.subcategory, o.sales_channel, o.quantity,
        o.unit_price, o.gross_revenue, o.discount_pct, o.discount_amount,
        o.net_revenue, o.cogs, o.gross_profit, o.gross_margin_pct, o.delivery_status
    FROM fact_sales_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN dim_products p ON o.product_id = p.product_id
""", conn)
conn.close()

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Color palette (Corporate Navy & Slate)
NAVY_HEADER = "1B365D"
ACCENT_BLUE = "2B547E"
LIGHT_BLUE = "E6EEF8"
WHITE = "FFFFFF"
GRAY_BG = "F4F6F9"
BORDER_GRAY = "D1D5DB"

thin_border = Border(
    left=Side(style='thin', color=BORDER_GRAY),
    right=Side(style='thin', color=BORDER_GRAY),
    top=Side(style='thin', color=BORDER_GRAY),
    bottom=Side(style='thin', color=BORDER_GRAY)
)
double_bottom_border = Border(
    left=Side(style='thin', color=BORDER_GRAY),
    right=Side(style='thin', color=BORDER_GRAY),
    top=Side(style='thin', color=BORDER_GRAY),
    bottom=Side(style='double', color='000000')
)

# =====================================================================
# SHEET 1: EXECUTIVE SUMMARY
# =====================================================================
ws_exec = wb.create_sheet(title="Executive_Summary")
ws_exec.views.sheetView[0].showGridLines = True

# Title banner
ws_exec.merge_cells("B2:J3")
title_cell = ws_exec["B2"]
title_cell.value = "ENTERPRISE BUSINESS PERFORMANCE & DECISION INTELLIGENCE"
title_cell.font = Font(name="Calibri", size=18, bold=True, color=WHITE)
title_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
title_cell.alignment = Alignment(horizontal="center", vertical="center")

ws_exec.merge_cells("B4:J4")
sub_cell = ws_exec["B4"]
sub_cell.value = "C-Suite Financial & Operational Performance Model | Period: 2022 - 2024"
sub_cell.font = Font(name="Calibri", size=11, italic=True, color="4B5563")
sub_cell.alignment = Alignment(horizontal="center", vertical="center")

# KPI Summary Cards setup
cards_meta = [
    ("TOTAL NET REVENUE", "=SUM(Transactions_Data!N:N)", "$#,##0", "B", "C", NAVY_HEADER),
    ("COST OF GOODS SOLD", "=SUM(Transactions_Data!O:O)", "$#,##0", "D", "E", "991B1B"),
    ("GROSS PROFIT", "=SUM(Transactions_Data!P:P)", "$#,##0", "F", "G", "065F46"),
    ("GROSS MARGIN %", "=F7/B7", "0.0%", "H", "H", NAVY_HEADER),
    ("TOTAL ORDERS", "=COUNTA(Transactions_Data!A:A)-1", "#,##0", "I", "I", "1F2937"),
    ("AVG ORDER VALUE", "=B7/I7", "$#,##0", "J", "J", "1F2937"),
]

for title, formula, fmt, col1, col2, text_color in cards_meta:
    if col1 != col2:
        ws_exec.merge_cells(f"{col1}6:{col2}6")
        ws_exec.merge_cells(f"{col1}7:{col2}7")
    
    c_title = ws_exec[f"{col1}6"]
    c_title.value = title
    c_title.font = Font(name="Calibri", size=9, bold=True, color="6B7280")
    c_title.alignment = Alignment(horizontal="center", vertical="center")
    
    c_val = ws_exec[f"{col1}7"]
    c_val.value = formula
    c_val.font = Font(name="Calibri", size=15, bold=True, color=text_color)
    c_val.number_format = fmt
    c_val.alignment = Alignment(horizontal="center", vertical="center")

card_cols = ["B", "C", "D", "E", "F", "G", "H", "I", "J"]
for col in card_cols:
    for row in [6, 7]:
        ws_exec[f"{col}{row}"].fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
        ws_exec[f"{col}{row}"].border = thin_border

# Annual Comparative Table (2022 vs 2023 vs 2024)
ws_exec["B10"].value = "ANNUAL FINANCIAL PERFORMANCE & GROWTH"
ws_exec["B10"].font = Font(name="Calibri", size=13, bold=True, color=NAVY_HEADER)

annual_headers = ["Financial Metric", "FY 2022", "FY 2023", "FY 2024", "3-Yr Total", "YoY (23-24) Growth"]
for c_idx, h in enumerate(annual_headers, start=2):
    cell = ws_exec.cell(row=11, column=c_idx, value=h)
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left")
    cell.border = thin_border

# Metrics Rows
fin_rows = [
    ("Gross Revenue", "=SUMIFS(Transactions_Data!K:K, Transactions_Data!B:B, \">=2022-01-01\", Transactions_Data!B:B, \"<=2022-12-31\")",
     "=SUMIFS(Transactions_Data!K:K, Transactions_Data!B:B, \">=2023-01-01\", Transactions_Data!B:B, \"<=2023-12-31\")",
     "=SUMIFS(Transactions_Data!K:K, Transactions_Data!B:B, \">=2024-01-01\", Transactions_Data!B:B, \"<=2024-12-31\")", "$#,##0"),
    ("Discounts Given", "=SUMIFS(Transactions_Data!M:M, Transactions_Data!B:B, \">=2022-01-01\", Transactions_Data!B:B, \"<=2022-12-31\")",
     "=SUMIFS(Transactions_Data!M:M, Transactions_Data!B:B, \">=2023-01-01\", Transactions_Data!B:B, \"<=2023-12-31\")",
     "=SUMIFS(Transactions_Data!M:M, Transactions_Data!B:B, \">=2024-01-01\", Transactions_Data!B:B, \"<=2024-12-31\")", "$#,##0"),
    ("Net Revenue", "=C12-C13", "=D12-D13", "=E12-E13", "$#,##0"),
    ("Cost of Goods Sold (COGS)", "=SUMIFS(Transactions_Data!O:O, Transactions_Data!B:B, \">=2022-01-01\", Transactions_Data!B:B, \"<=2022-12-31\")",
     "=SUMIFS(Transactions_Data!O:O, Transactions_Data!B:B, \">=2023-01-01\", Transactions_Data!B:B, \"<=2023-12-31\")",
     "=SUMIFS(Transactions_Data!O:O, Transactions_Data!B:B, \">=2024-01-01\", Transactions_Data!B:B, \"<=2024-12-31\")", "$#,##0"),
    ("Gross Profit", "=C14-C15", "=D14-D15", "=E14-E15", "$#,##0"),
    ("Gross Margin %", "=C16/C14", "=D16/D14", "=E16/E14", "0.0%"),
    ("Operating Expenses (OpEx)", 9200000, 10100000, 11023332, "$#,##0"),
    ("Operating Income (EBITDA)", "=C16-C18", "=D16-D18", "=E16-E18", "$#,##0"),
    ("Operating Margin %", "=C19/C14", "=D19/D14", "=E19/E14", "0.0%")
]

for r_idx, (m_label, f_22, f_23, f_24, fmt) in enumerate(fin_rows, start=12):
    ws_exec.cell(row=r_idx, column=2, value=m_label).font = Font(name="Calibri", bold=("Margin" in m_label or "Income" in m_label or "Net" in m_label))
    c22 = ws_exec.cell(row=r_idx, column=3, value=f_22)
    c23 = ws_exec.cell(row=r_idx, column=4, value=f_23)
    c24 = ws_exec.cell(row=r_idx, column=5, value=f_24)
    c_tot = ws_exec.cell(row=r_idx, column=6, value=f"=IF(ISNUMBER(SEARCH(\"%\",B{r_idx})),AVERAGE(C{r_idx}:E{r_idx}),SUM(C{r_idx}:E{r_idx}))")
    c_yoy = ws_exec.cell(row=r_idx, column=7, value=f"=(E{r_idx}-D{r_idx})/D{r_idx}")
    
    for c in [c22, c23, c24, c_tot]:
        c.number_format = fmt
        c.alignment = Alignment(horizontal="right")
        c.border = thin_border
    
    c_yoy.number_format = "+0.0%;-0.0%;0.0%"
    c_yoy.alignment = Alignment(horizontal="right")
    c_yoy.border = thin_border
    ws_exec.cell(row=r_idx, column=2).border = thin_border
    
    if "Margin" in m_label or "Income" in m_label:
        for c in [ws_exec.cell(row=r_idx, column=col) for col in range(2, 8)]:
            c.fill = PatternFill(start_color=GRAY_BG, end_color=GRAY_BG, fill_type="solid")
            c.font = Font(name="Calibri", bold=True)


# =====================================================================
# SHEET 2: CATEGORY PERFORMANCE
# =====================================================================
ws_cat = wb.create_sheet(title="Category_Performance")
ws_cat.views.sheetView[0].showGridLines = True

ws_cat["B2"].value = "PRODUCT CATEGORY & MARGIN EFFICIENCY ANALYSIS"
ws_cat["B2"].font = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)

cat_headers = ["Category", "Orders Count", "Units Sold", "Net Revenue ($)", "COGS ($)", "Gross Profit ($)", "Gross Margin %", "Avg Discount %"]
for c_idx, h in enumerate(cat_headers, start=2):
    cell = ws_cat.cell(row=4, column=c_idx, value=h)
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left")
    cell.border = thin_border

categories = sorted(df_orders["category"].unique())
for idx, cat in enumerate(categories, start=5):
    ws_cat.cell(row=idx, column=2, value=cat).font = Font(name="Calibri", bold=True)
    ws_cat.cell(row=idx, column=3, value=f'=COUNTIF(Transactions_Data!F:F, "{cat}")').number_format = "#,##0"
    ws_cat.cell(row=idx, column=4, value=f'=SUMIF(Transactions_Data!F:F, "{cat}", Transactions_Data!I:I)').number_format = "#,##0"
    ws_cat.cell(row=idx, column=5, value=f'=SUMIF(Transactions_Data!F:F, "{cat}", Transactions_Data!N:N)').number_format = "$#,##0"
    ws_cat.cell(row=idx, column=6, value=f'=SUMIF(Transactions_Data!F:F, "{cat}", Transactions_Data!O:O)').number_format = "$#,##0"
    ws_cat.cell(row=idx, column=7, value=f'=E{idx}-F{idx}').number_format = "$#,##0"
    ws_cat.cell(row=idx, column=8, value=f'=G{idx}/E{idx}').number_format = "0.0%"
    ws_cat.cell(row=idx, column=9, value=f'=AVERAGEIF(Transactions_Data!F:F, "{cat}", Transactions_Data!L:L)').number_format = "0.0%"
    
    for c_idx in range(2, 10):
        cell = ws_cat.cell(row=idx, column=c_idx)
        cell.border = thin_border
        if c_idx > 2:
            cell.alignment = Alignment(horizontal="right")

tot_row = len(categories) + 5
ws_cat.cell(row=tot_row, column=2, value="Total / Enterprise Average").font = Font(name="Calibri", bold=True)
ws_cat.cell(row=tot_row, column=3, value=f"=SUM(C5:C{tot_row-1})").number_format = "#,##0"
ws_cat.cell(row=tot_row, column=4, value=f"=SUM(D5:D{tot_row-1})").number_format = "#,##0"
ws_cat.cell(row=tot_row, column=5, value=f"=SUM(E5:E{tot_row-1})").number_format = "$#,##0"
ws_cat.cell(row=tot_row, column=6, value=f"=SUM(F5:F{tot_row-1})").number_format = "$#,##0"
ws_cat.cell(row=tot_row, column=7, value=f"=SUM(G5:G{tot_row-1})").number_format = "$#,##0"
ws_cat.cell(row=tot_row, column=8, value=f"=G{tot_row}/E{tot_row}").number_format = "0.0%"
ws_cat.cell(row=tot_row, column=9, value=f"=AVERAGE(I5:I{tot_row-1})").number_format = "0.0%"

for c_idx in range(2, 10):
    c = ws_cat.cell(row=tot_row, column=c_idx)
    c.font = Font(name="Calibri", bold=True)
    c.fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
    c.border = double_bottom_border
    if c_idx > 2:
        c.alignment = Alignment(horizontal="right")


# =====================================================================
# SHEET 3: REGIONAL ANALYSIS
# =====================================================================
ws_reg = wb.create_sheet(title="Regional_Analysis")
ws_reg.views.sheetView[0].showGridLines = True

ws_reg["B2"].value = "GEOGRAPHIC REGIONAL PERFORMANCE & MARKET SHARE"
ws_reg["B2"].font = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)

reg_headers = ["Region", "Orders", "Net Revenue ($)", "Revenue Share %", "Gross Profit ($)", "Profit Share %", "Gross Margin %"]
for c_idx, h in enumerate(reg_headers, start=2):
    cell = ws_reg.cell(row=4, column=c_idx, value=h)
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left")
    cell.border = thin_border

regions = sorted(df_orders["region"].unique())
for idx, reg in enumerate(regions, start=5):
    ws_reg.cell(row=idx, column=2, value=reg).font = Font(name="Calibri", bold=True)
    ws_reg.cell(row=idx, column=3, value=f'=COUNTIF(Transactions_Data!C:C, "{reg}")').number_format = "#,##0"
    ws_reg.cell(row=idx, column=4, value=f'=SUMIF(Transactions_Data!C:C, "{reg}", Transactions_Data!N:N)').number_format = "$#,##0"
    ws_reg.cell(row=idx, column=5, value=f'=D{idx}/$D$9').number_format = "0.0%"
    ws_reg.cell(row=idx, column=6, value=f'=SUMIF(Transactions_Data!C:C, "{reg}", Transactions_Data!P:P)').number_format = "$#,##0"
    ws_reg.cell(row=idx, column=7, value=f'=F{idx}/$F$9').number_format = "0.0%"
    ws_reg.cell(row=idx, column=8, value=f'=F{idx}/D{idx}').number_format = "0.0%"
    
    for c_idx in range(2, 9):
        cell = ws_reg.cell(row=idx, column=c_idx)
        cell.border = thin_border
        if c_idx > 2:
            cell.alignment = Alignment(horizontal="right")

ws_reg.cell(row=9, column=2, value="Global Total").font = Font(name="Calibri", bold=True)
ws_reg.cell(row=9, column=3, value="=SUM(C5:C8)").number_format = "#,##0"
ws_reg.cell(row=9, column=4, value="=SUM(D5:D8)").number_format = "$#,##0"
ws_reg.cell(row=9, column=5, value="=SUM(E5:E8)").number_format = "0.0%"
ws_reg.cell(row=9, column=6, value="=SUM(F5:F8)").number_format = "$#,##0"
ws_reg.cell(row=9, column=7, value="=SUM(G5:G8)").number_format = "0.0%"
ws_reg.cell(row=9, column=8, value="=F9/D9").number_format = "0.0%"

for c_idx in range(2, 9):
    c = ws_reg.cell(row=9, column=c_idx)
    c.font = Font(name="Calibri", bold=True)
    c.fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
    c.border = double_bottom_border
    if c_idx > 2:
        c.alignment = Alignment(horizontal="right")


# =====================================================================
# SHEET 4: WHAT-IF SCENARIO MODELER
# =====================================================================
ws_whatif = wb.create_sheet(title="Scenario_Modeler")
ws_whatif.views.sheetView[0].showGridLines = True

ws_whatif["B2"].value = "EXECUTIVE WHAT-IF SENSITIVITY MODELER"
ws_whatif["B2"].font = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)

ws_whatif["B3"].value = "Simulate impact of Price Adjustments and Discount Policy Governance on Enterprise EBITDA"
ws_whatif["B3"].font = Font(name="Calibri", size=10, italic=True, color="6B7280")

# Input Parameters block
ws_whatif["B5"].value = "BASELINE PARAMETERS"
ws_whatif["B5"].font = Font(name="Calibri", size=11, bold=True, color=NAVY_HEADER)
ws_whatif["B6"].value = "Baseline Net Revenue ($)"
ws_whatif["C6"].value = "=Executive_Summary!B7"
ws_whatif["C6"].number_format = "$#,##0"

ws_whatif["B7"].value = "Baseline COGS ($)"
ws_whatif["C7"].value = "=Executive_Summary!D7"
ws_whatif["C7"].number_format = "$#,##0"

ws_whatif["B8"].value = "Baseline OpEx ($)"
ws_whatif["C8"].value = 30323332
ws_whatif["C8"].number_format = "$#,##0"

ws_whatif["B9"].value = "Baseline Operating Income (EBITDA)"
ws_whatif["C9"].value = "=C6-C7-C8"
ws_whatif["C9"].number_format = "$#,##0"

for r in range(6, 10):
    ws_whatif[f"B{r}"].border = thin_border
    ws_whatif[f"C{r}"].border = thin_border
    ws_whatif[f"C{r}"].font = Font(name="Calibri", bold=True)

# Scenario Grid (Price Sensitivity vs Discount Optimization)
ws_whatif["B12"].value = "SENSITIVITY MATRIX: PROJECTED ENTERPRISE EBITDA ($M)"
ws_whatif["B12"].font = Font(name="Calibri", size=12, bold=True, color=NAVY_HEADER)

discount_adjustments = [-0.05, -0.02, 0.00, 0.02, 0.05] # Change in discount rate
price_adjustments = [-0.10, -0.05, 0.00, 0.05, 0.10] # Change in base price

ws_whatif["B14"].value = "Price Change ↓ / Discount Change →"
ws_whatif["B14"].font = Font(name="Calibri", size=9, bold=True, color=WHITE)
ws_whatif["B14"].fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
ws_whatif["B14"].border = thin_border

for c_idx, d_chg in enumerate(discount_adjustments, start=3):
    cell = ws_whatif.cell(row=14, column=c_idx, value=f"{d_chg:+.0%}")
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center")
    cell.border = thin_border

for r_idx, p_chg in enumerate(price_adjustments, start=15):
    r_hdr = ws_whatif.cell(row=r_idx, column=2, value=f"{p_chg:+.0%}")
    r_hdr.font = Font(name="Calibri", size=10, bold=True)
    r_hdr.alignment = Alignment(horizontal="center")
    r_hdr.fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
    r_hdr.border = thin_border
    
    for c_idx, d_chg in enumerate(discount_adjustments, start=3):
        # Formula: (BaseRev * (1 + PriceChg) * (1 - DiscountChg) - BaseCOGS - BaseOpEx) / 1e6
        cell = ws_whatif.cell(row=r_idx, column=c_idx, 
                              value=f"=($C$6*(1+{p_chg})*(1-{d_chg})-$C$7-$C$8)/1000000")
        cell.number_format = "$#,##0.0\"M\""
        cell.alignment = Alignment(horizontal="right")
        cell.border = thin_border
        if p_chg == 0.0 and d_chg == 0.0:
            cell.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Baseline highlighted
            cell.font = Font(name="Calibri", bold=True)


# =====================================================================
# SHEET 5: TRANSACTIONS DATA
# =====================================================================
ws_data = wb.create_sheet(title="Transactions_Data")
ws_data.views.sheetView[0].showGridLines = True

headers = list(df_orders.columns)
for c_idx, h in enumerate(headers, start=1):
    cell = ws_data.cell(row=1, column=c_idx, value=h.replace("_", " ").title())
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center")

# Write sample rows (top 1000 rows for Excel model performance and compactness)
sample_orders = df_orders.head(2000)
for r_idx, row in enumerate(sample_orders.itertuples(index=False), start=2):
    for c_idx, val in enumerate(row, start=1):
        cell = ws_data.cell(row=r_idx, column=c_idx, value=val)
        if headers[c_idx-1] in ["unit_price", "gross_revenue", "discount_amount", "net_revenue", "cogs", "gross_profit"]:
            cell.number_format = "$#,##0.00"
        elif headers[c_idx-1] in ["discount_pct"]:
            cell.number_format = "0.0%"
        elif headers[c_idx-1] in ["gross_margin_pct"]:
            cell.number_format = "0.0"


# =====================================================================
# SHEET 6: DATA DICTIONARY
# =====================================================================
ws_dict = wb.create_sheet(title="Data_Dictionary")
ws_dict.views.sheetView[0].showGridLines = True

ws_dict["B2"].value = "DATA DICTIONARY & BUSINESS FORMULA SPECIFICATION"
ws_dict["B2"].font = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)

dict_headers = ["Field / Metric Name", "Data Type", "Business Definition & Calculation Formula", "Target Benchmark"]
for c_idx, h in enumerate(dict_headers, start=2):
    cell = ws_dict.cell(row=4, column=c_idx, value=h)
    cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
    cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    cell.alignment = Alignment(horizontal="center" if c_idx > 2 else "left")
    cell.border = thin_border

dictionary_items = [
    ("Gross Revenue", "Currency", "Quantity * Base Catalog Unit Price before discretionary discounts", "Top-line volume"),
    ("Discount Amount", "Currency", "Gross Revenue * Approved Discount Percentage", "< 12% across channels"),
    ("Net Revenue", "Currency", "Gross Revenue - Discount Amount (Recognized Top-line)", "Core Revenue target"),
    ("COGS", "Currency", "Direct unit cost of hardware, cloud compute, or third-party engineering * Quantity", "Direct cost baseline"),
    ("Gross Profit", "Currency", "Net Revenue - COGS", "Value creation metric"),
    ("Gross Margin %", "Percentage", "(Gross Profit / Net Revenue) * 100", "> 52.0% enterprise hurdle"),
    ("Operating Expenses (OpEx)", "Currency", "Selling, General & Admin (SG&A) + R&D + Customer Support + IT Ops", "< 20% of Net Revenue"),
    ("Operating Income (EBITDA)", "Currency", "Gross Profit - Operating Expenses", "Profitability benchmark"),
    ("Operating Margin %", "Percentage", "(Operating Income / Net Revenue) * 100", "> 35.0% enterprise benchmark"),
    ("On-Time Delivery Rate", "Percentage", "(Orders Delivered On-Time / Total Dispatched Orders) * 100", "> 92.0% SLA")
]

for idx, item in enumerate(dictionary_items, start=5):
    for c_idx, val in enumerate(item, start=2):
        cell = ws_dict.cell(row=idx, column=c_idx, value=val)
        cell.border = thin_border
        if c_idx == 2:
            cell.font = Font(name="Calibri", bold=True)

# Adjust column widths across all sheets
for ws in wb.worksheets:
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col[:30])
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

wb.save(EXCEL_PATH)
print(f"Advanced Excel Model successfully created at: {EXCEL_PATH}")
