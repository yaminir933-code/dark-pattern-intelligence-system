-- ============================================================
-- Dark Pattern Intelligence System (DPIS)
-- Useful SQL Queries for Analysis & Power BI
-- ============================================================

-- ============================================================
-- 1. GET LATEST DPRS SCORE FOR ALL WEBSITES
-- ============================================================
SELECT
    w.name AS website,
    r.dprs_score,
    r.compliance_status,
    r.total_patterns,
    r.scan_date
FROM risk_scores r
JOIN websites w ON r.website_id = w.id
WHERE r.scan_date = (SELECT MAX(scan_date) FROM risk_scores WHERE website_id = r.website_id)
ORDER BY r.dprs_score DESC;


-- ============================================================
-- 2. TOP 10 MOST COMMON DARK PATTERNS ACROSS ALL SITES
-- ============================================================
SELECT
    pattern_name,
    pattern_type,
    severity,
    COUNT(*) AS total_occurrences
FROM dark_patterns
GROUP BY pattern_name, pattern_type, severity
ORDER BY total_occurrences DESC
LIMIT 10;


-- ============================================================
-- 3. DARK PATTERN COUNT BY WEBSITE AND SEVERITY
-- ============================================================
SELECT
    w.name AS website,
    dp.severity,
    COUNT(*) AS count
FROM dark_patterns dp
JOIN websites w ON dp.website_id = w.id
GROUP BY w.name, dp.severity
ORDER BY w.name, dp.severity;


-- ============================================================
-- 4. WHICH PAGE TYPE HAS MOST DARK PATTERNS?
-- (checkout pages are usually the worst)
-- ============================================================
SELECT
    sp.page_type,
    COUNT(dp.id) AS pattern_count,
    AVG(dp.confidence) AS avg_confidence
FROM dark_patterns dp
JOIN scraped_pages sp ON dp.page_id = sp.id
GROUP BY sp.page_type
ORDER BY pattern_count DESC;


-- ============================================================
-- 5. DPRS TREND OVER TIME (for Power BI line chart)
-- ============================================================
SELECT
    w.name AS website,
    r.scan_date,
    r.dprs_score
FROM risk_scores r
JOIN websites w ON r.website_id = w.id
ORDER BY w.name, r.scan_date;


-- ============================================================
-- 6. HIGH SEVERITY PATTERNS ONLY
-- ============================================================
SELECT
    w.name AS website,
    dp.pattern_name,
    dp.evidence,
    dp.detected_at
FROM dark_patterns dp
JOIN websites w ON dp.website_id = w.id
WHERE dp.severity = 'HIGH'
ORDER BY dp.detected_at DESC;


-- ============================================================
-- 7. WEBSITE COMPLIANCE SUMMARY (for Power BI KPI cards)
-- ============================================================
SELECT
    compliance_status,
    COUNT(*) AS website_count
FROM (
    SELECT DISTINCT ON (website_id) website_id, compliance_status
    FROM risk_scores
    ORDER BY website_id, scan_date DESC
) latest
GROUP BY compliance_status;


-- ============================================================
-- 8. CALCULATE DPRS SCORE (run after each scan)
-- ============================================================
WITH pattern_counts AS (
    SELECT
        website_id,
        SUM(CASE WHEN severity = 'HIGH'   THEN 10 ELSE 0 END) AS high_weighted,
        SUM(CASE WHEN severity = 'MEDIUM' THEN  5 ELSE 0 END) AS medium_weighted,
        SUM(CASE WHEN severity = 'LOW'    THEN  2 ELSE 0 END) AS low_weighted,
        COUNT(*) AS total_patterns
    FROM dark_patterns
    GROUP BY website_id
),
max_possible AS (
    SELECT website_id,
           (total_patterns * 10) AS max_score
    FROM pattern_counts
)
SELECT
    pc.website_id,
    ROUND(
        (pc.high_weighted + pc.medium_weighted + pc.low_weighted)::DECIMAL
        / NULLIF(mp.max_score, 0) * 100
    , 2) AS dprs_score
FROM pattern_counts pc
JOIN max_possible mp ON pc.website_id = mp.website_id;
