# 📊 Power BI & Tableau Business Intelligence Guide
**Dark Pattern Intelligence System (DPIS)**  
*Author: Yamini Reddy | Role: Data Analyst*

---

## 1. Overview & Business Intelligence Architecture

The **Dark Pattern Intelligence System (DPIS)** is built to support modern Business Intelligence (BI) tools including **Microsoft Power BI** and **Tableau**. It enables executives, compliance officers, and product managers to monitor deceptive UX practices in real time, benchmark competitors, and ensure legal adherence to **India's CCPA 2023 Guidelines** and the **Digital Personal Data Protection (DPDP) Act**.

```
┌─────────────────────────────────┐       ┌───────────────────────────────┐
│     DPIS Scraper & Classifier    │ ----> │    PostgreSQL / SQLite DB     │
│   (Python, BeautifulSoup, ML)   │       │  (Websites, Patterns, Scores) │
└─────────────────────────────────┘       └──────────────┬────────────────┘
                                                         │
                                    ┌────────────────────┴───────────────────┐
                                    │ Pre-Aggregated Analytical SQL Views   │
                                    │  • vw_website_summary                  │
                                    │  • vw_pattern_breakdown                │
                                    │  • vw_daily_trend                      │
                                    └────────────────────┬───────────────────┘
                                                         │
                                                         ▼
                                          ┌─────────────────────────────┐
                                          │   Power BI Desktop Report   │
                                          │  • Star Schema Modeling      │
                                          │  • DAX Calculated Measures  │
                                          │  • Executive Visual Dashboards│
                                          └─────────────────────────────┘
```

---

## 2. Data Model & Star Schema

For optimal performance in Power BI, data is structured into a **Star Schema** with clear separation of dimensions and facts:

```
                  ┌───────────────────────┐
                  │      dim_dates        │
                  │ ───────────────────── │
                  │ DateKey (PK)          │
                  │ FullDate              │
                  │ WeekNumber, Month     │
                  └───────────┬───────────┘
                              │ 1
                              │
                              │ *
┌───────────────────────┐     │     ┌───────────────────────┐
│     dim_websites      │     │     │   dim_pattern_types   │
│ ───────────────────── │     │     │ ───────────────────── │
│ website_id (PK)       │     │     │ pattern_type_id (PK)  │
│ website_name          │     │     │ pattern_name          │
│ category              │     │     │ category              │
│ country               │     │     │ legal_classification  │
└───────────┬───────────┘     │     └───────────┬───────────┘
            │ 1               │                 │ 1
            │                 │                 │
            │ *               │ *               │ *
┌───────────┴─────────────────┴─────────────────┴───────────┐
│                    fact_dark_patterns                     │
│ ───────────────────────────────────────────────────────── │
│ pattern_id (PK)                                           │
│ website_id (FK)                                           │
│ DateKey (FK)                                              │
│ pattern_type_id (FK)                                      │
│ severity (HIGH / MEDIUM / LOW)                            │
│ severity_weight (3 / 2 / 1)                               │
│ confidence_score                                          │
│ evidence_text                                             │
└───────────────────────────────────────────────────────────┘
```

### Table Relationships
1. `dim_websites (1)` ─── `fact_dark_patterns (*)` on `website_id`
2. `dim_pattern_types (1)` ─── `fact_dark_patterns (*)` on `pattern_type_id`
3. `dim_dates (1)` ─── `fact_dark_patterns (*)` on `DateKey`
4. `dim_websites (1)` ─── `fact_risk_scores (*)` on `website_id`

---

## 3. Connecting Power BI to the Database

### Option A: Direct Connection to PostgreSQL (Neon Cloud)
1. Open **Power BI Desktop**.
2. Click **Get Data** > **PostgreSQL database**.
3. In the Server field, enter your Neon Cloud host (e.g. `ep-xyz.ap-southeast-1.aws.neon.tech`).
4. In Database, enter `dpis_db`.
5. Under Data Connectivity mode, select **Import** (recommended for DAX performance) or **DirectQuery** (for real-time live telemetry).
6. Enter username and password from your `.env` file.
7. Select the views:
   - `vw_website_summary`
   - `vw_pattern_breakdown`
   - `vw_daily_trend`

### Option B: Import via Generated Excel / CSV Files
1. In Power BI, click **Get Data** > **Excel Workbook**.
2. Select `data/excel/executive_mis_report.xlsx` or `data/excel/website_scores.xlsx`.
3. Choose all sheets:
   - `Executive MIS Dashboard`
   - `Pattern Pivot Cross-Tab`
   - `Website Risk Benchmark`
   - `Weekly MIS Remediation`
4. Click **Load**.

---

## 4. DAX Measures Library (Formulas Ready to Use)

Paste these DAX measures directly into Power BI Modeling tab:

### 1. Total Patterns Detected
```dax
Total Patterns Detected = COUNT(fact_dark_patterns[pattern_id])
```

### 2. High-Severity Critical Patterns
```dax
High Severity Violations = 
CALCULATE(
    COUNT(fact_dark_patterns[pattern_id]),
    fact_dark_patterns[severity] = "HIGH"
)
```

### 3. Critical Severity Ratio %
```dax
Critical Ratio % = 
DIVIDE(
    [High Severity Violations],
    [Total Patterns Detected],
    0
)
```

### 4. Average DPRS Score
```dax
Average DPRS Score = 
AVERAGE(fact_risk_scores[dprs_score])
```

### 5. Compliance Rate %
```dax
Compliance Rate % = 
VAR CompliantCount = 
    CALCULATE(
        DISTINCTCOUNT(dim_websites[website_id]),
        fact_risk_scores[compliance_status] = "COMPLIANT"
    )
VAR TotalWebsites = DISTINCTCOUNT(dim_websites[website_id])
RETURN
    DIVIDE(CompliantCount, TotalWebsites, 0)
```

### 6. Dynamic Compliance Badge
```dax
Compliance Status Badge = 
SWITCH(
    TRUE(),
    [Average DPRS Score] >= 60, "🔴 NON-COMPLIANT",
    [Average DPRS Score] >= 30, "🟡 AT RISK",
    "🟢 COMPLIANT"
)
```

### 7. Week-over-Week (WoW) Pattern Growth
```dax
WoW Pattern Change % = 
VAR CurrentWeek = [Total Patterns Detected]
VAR PrevWeek = 
    CALCULATE(
        [Total Patterns Detected],
        DATEADD(dim_dates[FullDate], -7, DAY)
    )
RETURN
    DIVIDE(CurrentWeek - PrevWeek, PrevWeek, 0)
```

---

## 5. Dashboard Layout & Visuals Specification

### Page 1: Executive KPI & Risk Overview
- **Header Card Row**:
  - `Total Monitored Platforms` (Card)
  - `Active Violations` (Card with conditional red fill)
  - `Overall Compliance Rate %` (Card with green/amber indicator)
  - `High Severity Violations` (Card)
- **Gauge Chart**: `Average DPRS Score` with minimum=0, maximum=100, target=0, and warning thresholds at 30 and 60.
- **Clustered Bar Chart**: X-axis = `website_name`, Y-axis = `Total Patterns Detected`, Legend = `severity`.
- **Donut Chart**: Distribution of patterns by category (`Urgency`, `Misdirection`, `Scarcity`, `Obstruction`).

### Page 2: Platform Benchmarking & Deep Dive
- **Interactive Matrix Table**:
  - Rows: `website_name`
  - Columns: `pattern_type`
  - Values: `Count of Patterns`
  - Conditional Formatting: Background gradient fill (White to Soft Red for higher violations).
- **Scatter Plot (Risk Quadrant)**:
  - X-axis: `Scanned Page Count`
  - Y-axis: `Average DPRS Score`
  - Bubble Size: `High Severity Count`
  - Quadrant lines dividing High Risk vs Low Risk zones.

### Page 3: Trend & Remediation SLA Tracking
- **Area / Line Chart**: X-axis = `Date`, Y-axis = `Weekly Pattern Velocity`, Split by `severity`.
- **Stacked Bar Chart**: Departmental SLA Resolution % (`UX Design`, `Copywriting`, `Engineering`).
- **Slicers**: Sector filter, Date range slider, Severity checkboxes.

---

## 6. Refresh Scheduling & Governance

1. **Power BI Service Publishing**:
   - Click **Publish** in Power BI Desktop to deploy to Power BI Workspace.
2. **Gateway Configuration**:
   - For cloud PostgreSQL (Neon): Select **Cloud Connection** (no on-premises gateway required).
   - For SQLite: Set up an **On-premises Data Gateway (Standard Mode)** pointing to the folder path.
3. **Scheduled Refresh**:
   - Configure daily automatic refresh at **08:00 AM IST** to sync with the DPIS scraping schedule.
4. **Row-Level Security (RLS)**:
   - Configure roles for Legal (`ALL_DATA`) vs Platform Product Owners (`WEBSITE_SPECIFIC_DATA`) using DAX filter: `[website_name] = USERPRINCIPALNAME()`.

---
*Ready for immediate enterprise reporting and recruiter portfolio presentation.*
