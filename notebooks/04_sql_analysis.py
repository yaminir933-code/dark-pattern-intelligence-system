"""
============================================================
NOTEBOOK 04: Advanced SQL Analytics & Querying
Dark Pattern Intelligence System (DPIS)

Enterprise SQL Analysis showcasing core Data Analyst competencies:
  - Aggregations & Grouping (COUNT, AVG, SUM, GROUP BY, HAVING)
  - Multi-Table JOINs & Nested Subqueries
  - Analytical Window Functions (ROW_NUMBER, RANK, PARTITION BY)
  - Common Table Expressions (CTEs / WITH Clause)
  - Conditional CASE WHEN Aggregations & KPI Metrics
============================================================
"""

import sys
sys.path.append('..')

import pandas as pd
import numpy as np
from sqlalchemy import text
from src.db_connector import get_engine

print("=" * 65)
print("📊 DPIS NOTEBOOK 04: ADVANCED SQL ANALYTICS")
print("=" * 65)

engine = get_engine()

# Helper function to run and pretty print SQL queries
def run_query(title: str, query: str) -> pd.DataFrame:
    print(f"\n▶ {title}")
    print("-" * 60)
    print(f"SQL Query:\n{query.strip()}\n")
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        print(f"Results ({len(df)} rows):")
        print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"Query Execution Note: {e}")
        return pd.DataFrame()


# ─── Query 1: Basic Aggregations & Pattern Frequency ────────────────────────
q1 = """
SELECT 
    w.name AS website_name,
    COUNT(dp.id) AS total_patterns_detected,
    SUM(CASE WHEN dp.severity = 'HIGH' THEN 1 ELSE 0 END) AS high_severity_count,
    SUM(CASE WHEN dp.severity = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_severity_count,
    SUM(CASE WHEN dp.severity = 'LOW' THEN 1 ELSE 0 END) AS low_severity_count,
    ROUND(AVG(dp.confidence), 3) AS avg_confidence_score
FROM websites w
LEFT JOIN dark_patterns dp ON w.id = dp.website_id
GROUP BY w.name
ORDER BY total_patterns_detected DESC;
"""
df1 = run_query("Query 1: Website Dark Pattern Severity Breakdown (Aggregations & CASE WHEN)", q1)


# ─── Query 2: HAVING Filter on Aggregated Groups ────────────────────────────
q2 = """
SELECT 
    dp.pattern_type,
    dp.pattern_name,
    COUNT(*) AS occurrences,
    ROUND(AVG(dp.confidence), 3) AS avg_confidence
FROM dark_patterns dp
GROUP BY dp.pattern_type, dp.pattern_name
HAVING COUNT(*) >= 1
ORDER BY occurrences DESC;
"""
df2 = run_query("Query 2: Pattern Categories with Frequency Filter (HAVING Clause)", q2)


# ─── Query 3: Multi-Table JOIN with Subquery ────────────────────────────────
q3 = """
SELECT 
    w.name AS website_name,
    w.category,
    rs.dprs_score,
    rs.compliance_status,
    rs.scan_date
FROM websites w
INNER JOIN risk_scores rs ON w.id = rs.website_id
WHERE rs.dprs_score >= (
    SELECT AVG(dprs_score) FROM risk_scores
)
ORDER BY rs.dprs_score DESC;
"""
df3 = run_query("Query 3: Websites with Above-Average DPRS Risk (Subquery & JOIN)", q3)


# ─── Query 4: Analytical Window Functions (RANK & ROW_NUMBER) ───────────────
q4 = """
SELECT 
    w.name AS website_name,
    rs.scan_date,
    rs.dprs_score,
    rs.compliance_status,
    RANK() OVER (ORDER BY rs.dprs_score DESC) as overall_risk_rank,
    ROW_NUMBER() OVER (PARTITION BY rs.compliance_status ORDER BY rs.dprs_score DESC) as rank_within_status
FROM risk_scores rs
JOIN websites w ON rs.website_id = w.id
ORDER BY rs.dprs_score DESC
LIMIT 10;
"""
df4 = run_query("Query 4: Risk Ranking with Window Functions (RANK & PARTITION BY)", q4)


# ─── Query 5: Common Table Expression (CTE) for Executive KPI ───────────────
q5 = """
WITH WebsiteMetrics AS (
    SELECT 
        w.name AS website,
        COUNT(dp.id) AS total_detected,
        SUM(CASE WHEN dp.severity = 'HIGH' THEN 1 ELSE 0 END) AS high_sev
    FROM websites w
    LEFT JOIN dark_patterns dp ON w.id = dp.website_id
    GROUP BY w.name
),
AverageStats AS (
    SELECT AVG(total_detected) AS benchmark_avg FROM WebsiteMetrics
)
SELECT 
    wm.website,
    wm.total_detected,
    wm.high_sev,
    ROUND(a.benchmark_avg, 2) AS industry_benchmark,
    CASE 
        WHEN wm.total_detected > a.benchmark_avg THEN 'ABOVE BENCHMARK (HIGH CONCERN)'
        ELSE 'WITHIN BENCHMARK (ACCEPTABLE)'
    END AS risk_classification
FROM WebsiteMetrics wm
CROSS JOIN AverageStats a
ORDER BY wm.total_detected DESC;
"""
df5 = run_query("Query 5: Executive Risk Classification using Multi-Stage CTE (WITH Clause)", q5)


# ─── Step 6: Export Results ────────────────────────────────────────────────
if not df1.empty:
    df1.to_csv('../data/processed/sql_analysis_results.csv', index=False)
    print("\n" + "=" * 65)
    print("✅ SQL Analysis results exported to: ../data/processed/sql_analysis_results.csv")
    print("🎯 Advanced SQL Demonstration Complete!")
    print("=" * 65)
