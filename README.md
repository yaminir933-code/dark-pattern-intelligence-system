# 🛡️ Dark Pattern Intelligence System (DPIS)
### Enterprise E-Commerce UX Compliance, Statistical Analytics & MIS Reporting Platform

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-336791?logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-Business_Intelligence-F2C811?logo=powerbi&logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-Live_Dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Excel MIS](https://img.shields.io/badge/Excel-Advanced_MIS_Reporting-217346?logo=microsoftexcel&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> **An end-to-end data analytics and business intelligence platform that automatically detects manipulative UX dark patterns on Indian e-commerce platforms, computes a proprietary Dark Pattern Risk Score (DPRS), performs statistical hypothesis testing and EDA, executes advanced SQL analytics, and delivers executive MIS reports & dashboards.**

---

## 👨‍💻 Author & Portfolio Information
- **Author**: Yamini Reddy
- **Target Role**: Data Analyst / Business Analyst (Fresher / 0–1 Year Experience)
- **Core Competencies Demonstrated**: Data Cleaning, Data Validation, Statistical EDA, Advanced SQL, Excel MIS Reporting, Power BI Star Schema & DAX, Python Automation, Streamlit Dashboards.

---

## 🎯 Job-Ready Skill Mapping Matrix

This project was specifically designed to demonstrate every core requirement listed for enterprise **Data Analyst** roles:

| Job Posting Requirement | Demonstrated In Project | Project Artifact / Code File |
| :--- | :--- | :--- |
| **Collect Structured & Unstructured Data** | Web scraping pipeline with ethical request throttling, fake user-agents, parsing raw HTML/text. | [`src/scraper.py`](src/scraper.py)<br>[`notebooks/01_data_collection.py`](notebooks/01_data_collection.py) |
| **Data Validation & Quality Checks** | Null audits, duplicate detection, schema validation, Tukey's IQR outlier detection, business logic checks. | [`notebooks/02_data_validation.py`](notebooks/02_data_validation.py)<br>`data/processed/data_quality_report.csv` |
| **Data Cleaning & Preprocessing** | Standardizing case, cleaning text evidence, normalizing confidence intervals, handling missing values. | [`notebooks/02_data_validation.py`](notebooks/02_data_validation.py)<br>`data/processed/cleaned_patterns.csv` |
| **EDA & Statistical Analysis** | Chi-Square test of independence, Pearson correlation matrix, Linear Regression trendline, distributions. | [`notebooks/03_eda_analysis.py`](notebooks/03_eda_analysis.py)<br>`data/processed/eda_*.png` |
| **SQL (MySQL / PostgreSQL / SQLite)** | Aggregations, GROUP BY, HAVING, subqueries, Window Functions (`RANK()`, `PARTITION BY`), CTEs (`WITH`). | [`notebooks/04_sql_analysis.py`](notebooks/04_sql_analysis.py)<br>[`sql/schema.sql`](sql/schema.sql) |
| **Advanced Excel (Pivot, Formulas, MIS)** | Automated 4-sheet formatted workbook: Executive MIS, Cross-Tab (Pivot), Benchmark, Formulas (`SUM`, `IF`). | [`src/report_generator.py`](src/report_generator.py)<br>`data/excel/executive_mis_report.xlsx` |
| **Power BI / Tableau Familiarity** | Star Schema data model (Facts & Dimensions), pre-built analytical views, and copy-paste ready DAX formulas. | [`docs/POWER_BI_GUIDE.md`](docs/POWER_BI_GUIDE.md) |
| **MIS Reporting & Dashboards** | Live multi-tab Streamlit web application with KPI metric cards, departmental SLA tracker, and 1-click Excel download. | [`app/app.py`](app/app.py) (Tab 5: MIS Report) |
| **Actionable Business Insights** | Interpreting UX risk under India's CCPA 2023 Guidelines and DPDP Act with remediation recommendations. | [`notebooks/03_eda_analysis.py`](notebooks/03_eda_analysis.py) |

---

## 🏛️ System Architecture

```
                                  DATA COLLECTION & ETL
                ┌────────────────────────────────────────────────────────┐
                │  E-Commerce Platforms (Amazon, Flipkart, Meesho, etc.)  │
                └───────────────────────────┬────────────────────────────┘
                                            │ Python Scraper & Requests
                                            ▼
                                   RAW & CLEANED DATA
                ┌────────────────────────────────────────────────────────┐
                │   notebooks/02_data_validation.py (IQR Outlier, QA)    │
                └───────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                                 RELATIONAL STORAGE (SQL)
                ┌────────────────────────────────────────────────────────┐
                │      Neon PostgreSQL / Local SQLite (dpis_db.sqlite)   │
                │        • websites          • scraped_pages             │
                │        • dark_patterns     • risk_scores               │
                │        • analytical views (vw_website_summary, etc.)   │
                └───────┬───────────────────────────────────────┬────────┘
                        │                                       │
                        ▼                                       ▼
             BUSINESS INTELLIGENCE                     EXECUTIVE MIS & WEB
       ┌──────────────────────────────┐      ┌───────────────────────────────────┐
       │   Power BI Desktop Report    │      │    Streamlit Web App (app/app.py) │
       │   • Star Schema Data Model   │      │    • Tab 1: Overview Dashboard    │
       │   • DAX Measure Library      │      │    • Tab 2: Pattern Deep Dive     │
       │   • Executive Dashboards     │      │    • Tab 3: Trend Analysis        │
       └──────────────────────────────┘      │    • Tab 4: Live Website Scanner  │
                                             │    • Tab 5: MIS Executive Report  │
                                             └───────────────────────────────────┘
```

---

## 📂 Repository Layout

```
dark-pattern-intelligence-system/
├── app/
│   └── app.py                      # Streamlit interactive application (5 tabs)
├── data/
│   ├── excel/                      # Generated Excel workbooks & MIS exports
│   ├── processed/                  # Cleaned CSVs, QA reports, SQL outputs
│   └── raw/                        # Raw scraped data snapshots
├── docs/
│   ├── data_dictionary.md          # Complete data dictionary & schema definitions
│   └── POWER_BI_GUIDE.md           # Star Schema modeling, DAX formulas & visuals guide
├── notebooks/
│   ├── 01_data_collection.py       # Automated data scraping & database loading
│   ├── 02_data_validation.py       # QA checks, cleaning & IQR outlier detection
│   ├── 03_eda_analysis.py          # Chi-square test, Pearson correlation, regression
│   └── 04_sql_analysis.py          # Advanced SQL queries, window functions & CTEs
├── sql/
│   └── schema.sql                  # PostgreSQL schema, indexes, and Power BI views
├── src/
│   ├── classifier.py               # Dark pattern detection rules & NLP matcher
│   ├── db_connector.py             # Neon PostgreSQL & SQLite hybrid connector
│   ├── report_generator.py         # Multi-sheet openpyxl Excel & PDF generator
│   └── scraper.py                  # BeautifulSoup & request scraper
├── requirements.txt                # Python dependencies
├── run_dashboard.bat               # 1-click Windows launcher for Streamlit
└── README.md                       # Documentation & portfolio showcase
```

---

## 🚀 How to Run the Project Locally

### 1. Prerequisites
Ensure you have **Python 3.10+** (or Anaconda) installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Notebooks in Sequence
```bash
# Step 1: Collect & Scrape Data
python notebooks/01_data_collection.py

# Step 2: Validate, Clean & Detect Outliers
python notebooks/02_data_validation.py

# Step 3: Run Statistical EDA & Generate Visuals
python notebooks/03_eda_analysis.py

# Step 4: Run Advanced SQL Analytics
python notebooks/04_sql_analysis.py
```

### 4. Launch the Interactive MIS Streamlit App
Double-click `run_dashboard.bat` or run:
```bash
streamlit run app/app.py
```
Open your browser at `http://localhost:8501` to view:
- **Tab 1: Overview Dashboard** — DPRS risk distribution, top risky platforms, severity breakdown.
- **Tab 2: Pattern Deep Dive** — Evidence text inspection, keyword matching, confidence scores.
- **Tab 3: Trend Analysis** — Historical risk trajectory and pattern shifts over time.
- **Tab 4: Live Scanner** — Real-time dark pattern detection on any user-provided URL.
- **Tab 5: MIS Executive Report** — Compliance KPI cards, platform benchmarking table, departmental SLA resolution tracker, and 1-click download of the multi-sheet Excel MIS report.

---

## 📊 Sample Visuals & Outputs

| Analysis / Output | Description | Location |
| :--- | :--- | :--- |
| **Data Quality Report** | Field-level null audits, unique value counts, and rule verification. | `data/processed/data_quality_report.csv` |
| **EDA Charts** | Severity distribution, platform bar charts, evidence word cloud. | `data/processed/eda_*.png` |
| **Correlation Matrix** | Pearson correlation heatmap of severity vs confidence vs length. | `data/processed/eda_06_correlation_heatmap.png` |
| **Linear Regression** | Trendline showing risk factor interactions. | `data/processed/eda_07_regression_trend.png` |
| **SQL Analysis CSV** | Query results showing platform breakdowns and benchmark classifications. | `data/processed/sql_analysis_results.csv` |
| **Multi-Sheet MIS Excel** | 4-sheet formatted executive workbook with formulas and cross-tabs. | `data/excel/executive_mis_report.xlsx` |

---

## ⚖️ Regulatory Compliance Context
This platform is directly aligned with:
- **India Central Consumer Protection Authority (CCPA) 2023 Guidelines**: Prohibiting 13 specified dark patterns (False Urgency, Basket Sneaking, Confirm Shaming, Forced Actions, Subscription Traps, etc.).
- **Digital Personal Data Protection (DPDP) Act, 2023**: Mandating transparent, non-deceptive consent architecture.

---
*Built with passion by **Yamini Reddy** to empower ethical product design and data-driven compliance.*
