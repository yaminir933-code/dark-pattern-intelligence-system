# Client Delivery Charter & System Handover Manual
## Project: Dark Pattern Intelligence System (DPIS)
**Prepared for**: Client Stakeholders & Executive Reviewers  
**Author**: Yamini Reddy (Lead Data Analyst & Systems Architect)  
**Version**: 1.0.0 (Production Release)  
**Date**: August 2026  

---

## 1. Executive Summary & Deliverables

The **Dark Pattern Intelligence System (DPIS)** is an enterprise-grade web scraping, natural language processing (NLP), and compliance reporting engine designed to monitor, audit, and score deceptive UX design practices across e-commerce platforms.

### Handover Deliverables Included in this Package:
1. **Interactive Analytics Web App**: Streamlit dashboard with real-time URL scanning, metric filtering, heatmaps, and trend visualization (`app/app.py`).
2. **Master ETL & Automation Runner**: Unified CLI pipeline script (`src/run_pipeline.py`).
3. **Dual Relational Database**: PostgreSQL + SQLite fallback database schema with dynamic view abstractions (`src/db_connector.py`, `dpis_db.sqlite`).
4. **Automated Executive PDF & Excel Reports**:
   - `data/excel/website_scores.xlsx`
   - `data/excel/kpi_tracker.xlsx`
   - `data/excel/dark_pattern_audit_template.xlsx`
   - `data/excel/DPIS_Executive_Audit_Report.pdf`
5. **1-Click Local Windows Launcher**: `run_dashboard.bat`.

---

## 2. End-to-End System Architecture

```
                               ┌───────────────────────────┐
                               │ Target E-Commerce Websites │
                               └─────────────┬─────────────┘
                                             │
                                   Ethical Web Scraper
                                   (requests + bs4)
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   NLP Pattern Classifier  │
                               │ (Regex + Tag Classifier)  │
                               └─────────────┬─────────────┘
                                             │
                                     DPRS Scoring Engine
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   Dual SQL Storage Layer  │
                               │  (PostgreSQL / SQLite)    │
                               └─────────────┬─────────────┘
                                             │
                                 ┌───────────┴───────────┐
                                 ▼                       ▼
                     ┌───────────────────────┐ ┌──────────────────┐
                     │  Streamlit Web App    │ │ Automated Reports│
                     │  (Interactive UI)     │ │  (PDF & Excel)   │
                     └───────────────────────┘ └──────────────────┘
```

---

## 3. Dark Pattern Risk Score (DPRS) Methodology

The **Dark Pattern Risk Score (DPRS)** quantifies regulatory risk on a scale of **0.0 to 100.0**:

$$\text{DPRS} = \min\left(100, \, \frac{\sum (w_{\text{severity}} \times \text{Count}_{\text{patterns}})}{\text{Pages Scanned}} \times 20\right)$$

Where severity weights $w$ are assigned as:
- **HIGH Severity**: $3.0$ points (Fake Timers, Pre-checked Boxes, Hidden Subscriptions, Price Drip)
- **MEDIUM Severity**: $2.0$ points (Fake Scarcity, Confirm Shaming, Disguised Ads)
- **LOW Severity**: $1.0$ point (Mild urgency cues)

### Compliance Classification Thresholds:
* 🟢 **COMPLIANT** ($\text{DPRS} \le 30.0$): Platform adheres to ethical guidelines.
* 🟡 **AT RISK** ($30.1 \le \text{DPRS} \le 60.0$): Platform uses moderate deceptive tactics; remediation recommended.
* 🔴 **NON-COMPLIANT** ($\text{DPRS} > 60.0$): High density of critical dark patterns; high risk under CCPA guidelines.

---

## 4. Operational Guide for Clients

### Launching the Dashboard (1-Click)
Double-click `run_dashboard.bat` in Windows Explorer, or execute in terminal:
```bash
python -m streamlit run app/app.py
```

### Running the Full Pipeline & Refreshing Database
```bash
python src/run_pipeline.py --init-db
```

### Generating Executive PDF Audit Reports
```bash
python src/pdf_report_generator.py
```

---

## 5. Maintenance & Support

- **Database Maintenance**: Database views auto-recompute summary metrics on every insert.
- **Rule Expansion**: Additional dark pattern categories can be registered in `src/classifier.py` by adding keyword patterns to the classifier dictionary.
