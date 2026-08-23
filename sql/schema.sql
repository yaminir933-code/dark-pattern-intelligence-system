-- ============================================================
-- Dark Pattern Intelligence System (DPIS)
-- PostgreSQL Schema for Neon Cloud Database
-- ============================================================

-- Drop tables if they exist (for clean reset)
DROP TABLE IF EXISTS risk_scores CASCADE;
DROP TABLE IF EXISTS dark_patterns CASCADE;
DROP TABLE IF EXISTS scraped_pages CASCADE;
DROP TABLE IF EXISTS websites CASCADE;

-- ============================================================
-- TABLE 1: websites
-- Stores the list of e-commerce websites being tracked
-- ============================================================
CREATE TABLE websites (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    url             TEXT            NOT NULL UNIQUE,
    category        VARCHAR(50)     DEFAULT 'E-Commerce',
    country         VARCHAR(50)     DEFAULT 'India',
    is_active       BOOLEAN         DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT NOW(),
    updated_at      TIMESTAMP       DEFAULT NOW()
);

-- Insert the 5 target websites
INSERT INTO websites (name, url, category, country) VALUES
    ('Amazon India',  'https://www.amazon.in',   'E-Commerce', 'India'),
    ('Flipkart',      'https://www.flipkart.com', 'E-Commerce', 'India'),
    ('Meesho',        'https://www.meesho.com',   'E-Commerce', 'India'),
    ('Myntra',        'https://www.myntra.com',   'Fashion',    'India'),
    ('Snapdeal',      'https://www.snapdeal.com', 'E-Commerce', 'India');

-- ============================================================
-- TABLE 2: scraped_pages
-- Stores each individual page that was scraped
-- ============================================================
CREATE TABLE scraped_pages (
    id              SERIAL PRIMARY KEY,
    website_id      INT             REFERENCES websites(id) ON DELETE CASCADE,
    page_url        TEXT            NOT NULL,
    page_type       VARCHAR(50),    -- 'homepage' | 'product' | 'checkout' | 'search'
    scraped_at      TIMESTAMP       DEFAULT NOW(),
    status_code     INT,
    raw_content     TEXT,
    word_count      INT
);

-- ============================================================
-- TABLE 3: dark_patterns
-- Stores every dark pattern detected on each page
-- ============================================================
CREATE TABLE dark_patterns (
    id              SERIAL PRIMARY KEY,
    page_id         INT             REFERENCES scraped_pages(id) ON DELETE CASCADE,
    website_id      INT             REFERENCES websites(id) ON DELETE CASCADE,
    pattern_type    VARCHAR(100)    NOT NULL,
    pattern_name    VARCHAR(150)    NOT NULL,
    severity        VARCHAR(20)     CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
    evidence        TEXT,           -- Actual text/element found
    element_tag     VARCHAR(50),    -- HTML tag where found
    confidence      DECIMAL(4,2),   -- Detection confidence score (0.00-1.00)
    detected_at     TIMESTAMP       DEFAULT NOW()
);

-- ============================================================
-- TABLE 4: risk_scores
-- Stores DPRS (Dark Pattern Risk Score) per website per scan
-- ============================================================
CREATE TABLE risk_scores (
    id                  SERIAL PRIMARY KEY,
    website_id          INT             REFERENCES websites(id) ON DELETE CASCADE,
    dprs_score          DECIMAL(5,2),   -- 0 to 100
    total_pages_scanned INT             DEFAULT 0,
    total_patterns      INT             DEFAULT 0,
    high_severity       INT             DEFAULT 0,
    medium_severity     INT             DEFAULT 0,
    low_severity        INT             DEFAULT 0,
    compliance_status   VARCHAR(20)     CHECK (compliance_status IN ('COMPLIANT', 'AT RISK', 'NON-COMPLIANT')),
    scan_date           DATE            DEFAULT CURRENT_DATE,
    scored_at           TIMESTAMP       DEFAULT NOW()
);

-- ============================================================
-- VIEWS for Power BI Dashboard
-- ============================================================

-- View 1: Website Summary with latest DPRS
CREATE OR REPLACE VIEW vw_website_summary AS
SELECT
    w.name AS website_name,
    w.url,
    w.category,
    r.dprs_score,
    r.total_patterns,
    r.high_severity,
    r.medium_severity,
    r.low_severity,
    r.compliance_status,
    r.scan_date
FROM websites w
LEFT JOIN risk_scores r ON w.id = r.website_id
WHERE r.scan_date = (
    SELECT MAX(scan_date) FROM risk_scores WHERE website_id = w.id
);

-- View 2: Pattern breakdown by type
CREATE OR REPLACE VIEW vw_pattern_breakdown AS
SELECT
    w.name AS website_name,
    dp.pattern_name,
    dp.pattern_type,
    dp.severity,
    COUNT(*) AS occurrence_count,
    AVG(dp.confidence) AS avg_confidence
FROM dark_patterns dp
JOIN websites w ON dp.website_id = w.id
GROUP BY w.name, dp.pattern_name, dp.pattern_type, dp.severity
ORDER BY occurrence_count DESC;

-- View 3: Daily scan trend
CREATE OR REPLACE VIEW vw_daily_trend AS
SELECT
    w.name AS website_name,
    DATE(dp.detected_at) AS detection_date,
    dp.severity,
    COUNT(*) AS pattern_count
FROM dark_patterns dp
JOIN websites w ON dp.website_id = w.id
GROUP BY w.name, DATE(dp.detected_at), dp.severity
ORDER BY detection_date;

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX idx_dark_patterns_website ON dark_patterns(website_id);
CREATE INDEX idx_dark_patterns_severity ON dark_patterns(severity);
CREATE INDEX idx_dark_patterns_pattern_type ON dark_patterns(pattern_type);
CREATE INDEX idx_scraped_pages_website ON scraped_pages(website_id);
CREATE INDEX idx_risk_scores_website ON risk_scores(website_id);
CREATE INDEX idx_risk_scores_date ON risk_scores(scan_date);
