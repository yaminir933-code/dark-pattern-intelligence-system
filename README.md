# 🕵️ Dark Pattern Intelligence System (DPIS)

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-green?logo=postgresql)
![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-yellow?logo=powerbi)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **An end-to-end data analytics platform that automatically detects manipulative UX dark patterns on Indian e-commerce websites, computes a Dark Pattern Risk Score (DPRS), and visualizes compliance insights through Power BI and a live Streamlit dashboard.**

---

## 🎯 Problem Statement

Dark patterns are deceptive UX/UI design tactics that manipulate users into unintended actions — like hidden subscription charges, fake countdown timers, or pre-checked boxes. India's Consumer Protection Act and the EU's DSA now **legally mandate** detection and removal of such patterns.

This project builds an automated intelligence system to **detect, score, and report** dark patterns across major e-commerce platforms.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Collection | Python, BeautifulSoup, Selenium |
| Data Processing | Pandas, NumPy, NLTK, spaCy |
| Database | PostgreSQL (Neon Cloud) |
| Reporting | Excel (openpyxl), PDF (fpdf2) |
| Dashboard | Power BI Desktop |
| Web App | Streamlit |
| Deployment | Render |
| Version Control | GitHub |

---

## 📁 Project Structure

```
dark-pattern-intelligence-system/
├── data/
│   ├── raw/                    ← Scraped raw data
│   ├── processed/              ← Cleaned data
│   └── excel/                  ← Excel reports & templates
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_analysis.ipynb
│   ├── 04_dark_pattern_classifier.ipynb
│   ├── 05_database_load.ipynb
│   └── 06_reporting.ipynb
├── src/
│   ├── scraper.py
│   ├── classifier.py
│   ├── db_connector.py
│   └── report_generator.py
├── app/
│   ├── app.py                  ← Streamlit app
│   └── requirements.txt
├── powerbi/
│   └── dpis_dashboard.pbix
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── docs/
│   ├── project_documentation.md
│   ├── data_dictionary.md
│   └── user_guide.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🕵️ Dark Patterns Detected (12 Categories)

| # | Pattern | Severity |
|---|---------|---------|
| 1 | Fake Countdown Timer | 🔴 HIGH |
| 2 | Hidden Subscription | 🔴 HIGH |
| 3 | Pre-checked Boxes | 🔴 HIGH |
| 4 | Fake Scarcity ("Only X left") | 🟡 MEDIUM |
| 5 | Price Drip (hidden fees) | 🔴 HIGH |
| 6 | Roach Motel | 🔴 HIGH |
| 7 | Confirm Shaming | 🟡 MEDIUM |
| 8 | Disguised Ads | 🟡 MEDIUM |
| 9 | Friend Spam | 🟡 MEDIUM |
| 10 | Misleading Free Trial | 🔴 HIGH |
| 11 | Price Comparison Prevention | 🟢 LOW |
| 12 | Bait and Switch | 🔴 HIGH |

---

## 📊 Dark Pattern Risk Score (DPRS)

```
DPRS = (HIGH × 10 + MEDIUM × 5 + LOW × 2) / Total_Possible_Score × 100

Score Range:
  0–30   → 🟢 LOW RISK    (Compliant)
  31–60  → 🟡 MEDIUM RISK (Needs Improvement)
  61–100 → 🔴 HIGH RISK   (Non-Compliant)
```

---

## 🚀 How to Run

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/dark-pattern-intelligence-system.git
cd dark-pattern-intelligence-system
```

### 2. Create Virtual Environment (Anaconda)
```bash
conda create -n dpis python=3.11
conda activate dpis
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your Neon PostgreSQL credentials
```

### 4. Initialize Database
```bash
# Run schema.sql in your Neon PostgreSQL console
```

### 5. Run Notebooks in Order
```
notebooks/01_data_collection.ipynb
notebooks/02_data_cleaning.ipynb
...
```

### 6. Run Web App Locally
```bash
cd app
streamlit run app.py
```

---

## 📈 Results

- **5 websites scanned**: Amazon.in, Flipkart, Meesho, Myntra, Snapdeal
- **5,000+ pages analyzed**
- **12 dark pattern categories detected**
- **DPRS scores computed** for all websites
- **Power BI dashboard** with 4 pages of insights
- **Live web app** at: https://dpis-app.onrender.com

---

## 📋 Excel Reports

| File | Purpose |
|------|---------|
| `dark_pattern_audit_template.xlsx` | Manual audit worksheet |
| `kpi_tracker.xlsx` | Weekly KPI tracking with charts |
| `website_scores.xlsx` | Final DPRS scores with color coding |

---

## 👩‍💻 Author

**Yamini Reddy**  
Data Analyst | Python | SQL | Power BI | Excel  
[LinkedIn](#) | [GitHub](#)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
