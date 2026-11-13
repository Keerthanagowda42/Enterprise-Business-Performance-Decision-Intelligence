# Enterprise Business Intelligence Dashboard Wireframe & Visual Specification Guide

## 1. Visual Theme & Palette Design System
- **Primary Navy / Corporate**: `#1B365D` (Headers, Primary Cards, Primary Bar charts)
- **Secondary Slate Blue**: `#2B547E` (Data points, supporting charts)
- **Accent Emerald Green**: `#10B981` (Profit, Positive Growth, On-Time metrics)
- **Accent Crimson Alert**: `#EF4444` (Budget Overruns, Delayed Deliveries, Margin erosion)
- **Neutral Background**: `#F8FAFC`
- **Surface Cards**: `#FFFFFF` with soft drop shadow (`box-shadow: 0 2px 4px rgba(0,0,0,0.05)`)

---

## 2. 4-Page Power BI Architecture

### Page 1: C-Suite Executive Cockpit
- **Target Audience**: CEO, CFO, Board of Directors
- **Header Banner**: Dynamic Period Slicer (2022, 2023, 2024, YTD), Currency selector, Region Slicer.
- **Top Row KPI Cards (Multi-Row Cards)**:
  1. Net Revenue: `$170.2M` with YoY indicator badge `+14.8%`
  2. Gross Profit: `$93.6M` (Gross Margin: `55.0%`)
  3. Operating Income (EBITDA): `$63.3M` (EBITDA Margin: `37.2%`)
  4. Operating Expenses (OpEx): `$30.3M` (Variance vs Budget: `-$142k`)
  5. Total Orders & AOV: `15,000 Orders` | `$11,346 AOV`
- **Center Visual**: Line & Clustered Column Chart:
  - Columns: Monthly Net Revenue ($M)
  - Line: Monthly Gross Margin %
- **Right Visual**: Waterfall Chart:
  - Gross Revenue -> Discounts Given (-) -> COGS (-) -> Operating Expenses (-) -> Net EBITDA.
- **Bottom Left**: Product Category Profitability Bar Chart.
- **Bottom Right**: Regional Revenue Heat Table with sparklines.

---

### Page 2: Revenue, Sales Channels & Customer Segments
- **Target Audience**: VP of Sales, Chief Commercial Officer
- **Slicers**: Region, Customer Segment, Industry, Sales Channel.
- **Visual 1**: Donut Chart: Sales Channel Contribution (Direct Sales 45%, Partner 30%, Digital 15%, Inside Sales 10%).
- **Visual 2**: Stacked Bar Chart: Revenue by Customer Segment across Industries.
- **Visual 3**: Scatter Plot: Customer Acquisition Cost vs Customer Lifetime Value (CLV).
- **Visual 4**: Top 10 Enterprise Customer Accounts Matrix (Orders, Total Spend, Discount %, Profit Contribution).

---

### Page 3: Margin Health & Cost Optimization
- **Target Audience**: VP of Finance, Head of Procurement
- **Visual 1**: Treemap: Profit Contribution by Product Subcategory.
- **Visual 2**: OpEx Budget vs Actual Spend by Department (Waterfall / Variance Bar).
- **Visual 3**: Discount Rate vs Gross Margin Scatter Plot (Identifying discount abuse).
- **Visual 4**: Sensitivity / What-If Parameter Sliders:
  - Slider A: Unit Price Adjustment (-10% to +10%)
  - Slider B: Target Discount Reduction (-5% to +5%)
  - Dynamic KPI: Projected Incremental EBITDA.

---

### Page 4: Supply Chain & Operational Fulfillment
- **Target Audience**: Chief Operating Officer, VP of Supply Chain
- **Top KPI Cards**:
  1. Average Lead Time: `5.4 Days`
  2. On-Time Delivery Rate: `88.5%` (Target: `> 90%`)
  3. Delayed Shipment Rate: `8.1%`
  4. Cancellation Rate: `1.0%`
- **Visual 1**: Lead Time Distribution by Fulfillment Mode (Box Plot / Violin).
- **Visual 2**: On-Time Delivery Rate by Geographic Region (Clustered Bar).
- **Visual 3**: Bottleneck Analysis Table: Carrier / Fulfillment mode delayed shipments count.

