"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/db_connector.py

PostgreSQL (Neon) Database Connection Module
============================================================
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import pandas as pd
import sqlite3
try:
    import psycopg2
except ImportError:
    psycopg2 = None
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection_string() -> str:
    """Returns the Neon PostgreSQL connection string from .env, with SQLite fallback."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Build from individual parts
        host     = os.getenv("DB_HOST")
        port     = os.getenv("DB_PORT", "5432")
        dbname   = os.getenv("DB_NAME")
        user     = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        sslmode  = os.getenv("DB_SSLMODE", "require")
        if host and dbname and user and password:
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"
        else:
            # Fallback to local SQLite database
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sqlite_path = os.path.join(base_dir, "dpis_db.sqlite").replace('\\', '/')
            db_url = f"sqlite:///{sqlite_path}"
    return db_url


def get_engine():
    """Creates and returns a SQLAlchemy engine for Neon PostgreSQL or SQLite"""
    connection_string = get_connection_string()
    # SQLite requires some settings for threading if used with streamlit
    if connection_string.startswith("sqlite"):
        engine = create_engine(connection_string, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(connection_string)
    return engine


def get_psycopg2_connection():
    """Creates and returns a raw connection (psycopg2/psycopg for postgres, sqlite3 for sqlite)"""
    db_url = get_connection_string()
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        return sqlite3.connect(db_path)
    else:
        if psycopg2 is not None:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", 5432)),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                sslmode=os.getenv("DB_SSLMODE", "require")
            )
            return conn
        else:
            try:
                import psycopg
                conn = psycopg.connect(
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 5432)),
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    sslmode=os.getenv("DB_SSLMODE", "require")
                )
                return conn
            except ImportError:
                raise ImportError("Neither psycopg2 nor psycopg (v3) is installed. Please install one to connect to PostgreSQL.")



def test_connection() -> bool:
    """Tests the database connection — returns True if successful"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            # Fetch one to verify execution
            result.fetchone()
            db_url = get_connection_string()
            if db_url.startswith("sqlite"):
                print("✅ Local SQLite connection successful!")
            else:
                print("✅ Neon PostgreSQL connection successful!")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def init_db(force: bool = False):
    """Initializes the database schema (tables and views) depending on dialect."""
    db_url = get_connection_string()
    is_sqlite = db_url.startswith("sqlite")
    engine = get_engine()
    
    with engine.connect() as conn:
        if is_sqlite:
            # SQLite setup
            if force:
                conn.execute(text("DROP VIEW IF EXISTS vw_website_summary"))
                conn.execute(text("DROP VIEW IF EXISTS vw_pattern_breakdown"))
                conn.execute(text("DROP VIEW IF EXISTS vw_daily_trend"))
                conn.execute(text("DROP TABLE IF EXISTS risk_scores"))
                conn.execute(text("DROP TABLE IF EXISTS dark_patterns"))
                conn.execute(text("DROP TABLE IF EXISTS scraped_pages"))
                conn.execute(text("DROP TABLE IF EXISTS websites"))
                
            # Create tables
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS websites (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            VARCHAR(100)    NOT NULL,
                    url             TEXT            NOT NULL UNIQUE,
                    category        VARCHAR(50)     DEFAULT 'E-Commerce',
                    country         VARCHAR(50)     DEFAULT 'India',
                    is_active       BOOLEAN         DEFAULT 1,
                    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scraped_pages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id      INT             REFERENCES websites(id) ON DELETE CASCADE,
                    page_url        TEXT            NOT NULL,
                    page_type       VARCHAR(50),
                    scraped_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
                    status_code     INT,
                    raw_content     TEXT,
                    word_count      INT
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dark_patterns (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id         INT             REFERENCES scraped_pages(id) ON DELETE CASCADE,
                    website_id      INT             REFERENCES websites(id) ON DELETE CASCADE,
                    pattern_type    VARCHAR(100)    NOT NULL,
                    pattern_name    VARCHAR(150)    NOT NULL,
                    severity        VARCHAR(20)     CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
                    evidence        TEXT,
                    element_tag     VARCHAR(50),
                    confidence      DECIMAL(4,2),
                    detected_at     TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS risk_scores (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    website_id          INT             REFERENCES websites(id) ON DELETE CASCADE,
                    dprs_score          DECIMAL(5,2),
                    total_pages_scanned INT             DEFAULT 0,
                    total_patterns      INT             DEFAULT 0,
                    high_severity       INT             DEFAULT 0,
                    medium_severity     INT             DEFAULT 0,
                    low_severity        INT             DEFAULT 0,
                    compliance_status   VARCHAR(20)     CHECK (compliance_status IN ('COMPLIANT', 'AT RISK', 'NON-COMPLIANT')),
                    scan_date           DATE            DEFAULT (DATE('now')),
                    scored_at           TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert the 5 target websites
            conn.execute(text("""
                INSERT OR IGNORE INTO websites (id, name, url, category, country) VALUES
                    (1, 'Amazon India',  'https://www.amazon.in',   'E-Commerce', 'India'),
                    (2, 'Flipkart',      'https://www.flipkart.com', 'E-Commerce', 'India'),
                    (3, 'Meesho',        'https://www.meesho.com',   'E-Commerce', 'India'),
                    (4, 'Myntra',        'https://www.myntra.com',   'Fashion',    'India'),
                    (5, 'Snapdeal',      'https://www.snapdeal.com', 'E-Commerce', 'India')
            """))
            
            # Create Views
            conn.execute(text("DROP VIEW IF EXISTS vw_website_summary"))
            conn.execute(text("""
                CREATE VIEW vw_website_summary AS
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
                )
            """))
            
            conn.execute(text("DROP VIEW IF EXISTS vw_pattern_breakdown"))
            conn.execute(text("""
                CREATE VIEW vw_pattern_breakdown AS
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
                ORDER BY occurrence_count DESC
            """))
            
            conn.execute(text("DROP VIEW IF EXISTS vw_daily_trend"))
            conn.execute(text("""
                CREATE VIEW vw_daily_trend AS
                SELECT
                    w.name AS website_name,
                    DATE(dp.detected_at) AS detection_date,
                    dp.severity,
                    COUNT(*) AS pattern_count
                FROM dark_patterns dp
                JOIN websites w ON dp.website_id = w.id
                GROUP BY w.name, DATE(dp.detected_at), dp.severity
                ORDER BY detection_date
            """))
            
            # Create Indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_dark_patterns_website ON dark_patterns(website_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_dark_patterns_severity ON dark_patterns(severity)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_scraped_pages_website ON scraped_pages(website_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_risk_scores_website ON risk_scores(website_id)"))
            
            print("✅ SQLite database initialized successfully!")
            
        else:
            # PostgreSQL setup
            schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql", "schema.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r") as f:
                    schema_sql = f.read()
                # Split by semicolon and run each statement
                statements = schema_sql.split(";")
                for stmt in statements:
                    clean_stmt = stmt.strip()
                    if clean_stmt:
                        conn.execute(text(clean_stmt))
                print("✅ Neon PostgreSQL database schema executed successfully!")
            else:
                print("❌ schema.sql file not found!")


# ============================================================
# DATA LOADING FUNCTIONS
# ============================================================

def load_dataframe(query: str) -> pd.DataFrame:
    """
    Runs a SQL query and returns results as a pandas DataFrame.
    
    Args:
        query: SQL SELECT query string
        
    Returns:
        pd.DataFrame with query results
    """
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df


def insert_website(name: str, url: str, category: str = "E-Commerce", country: str = "India") -> int:
    """
    Inserts a new website record.
    
    Returns:
        id of the inserted website
    """
    engine = get_engine()
    with engine.begin() as conn:
        # Check if website already exists
        res = conn.execute(text("SELECT id FROM websites WHERE url = :url"), {"url": url})
        row = res.fetchone()
        if row:
            return row[0]

        # Insert new website
        conn.execute(
            text("""
                INSERT INTO websites (name, url, category, country)
                VALUES (:name, :url, :category, :country)
            """),
            {"name": name, "url": url, "category": category, "country": country}
        )
        
        # Get new id
        res = conn.execute(text("SELECT id FROM websites WHERE url = :url"), {"url": url})
        row = res.fetchone()
        return row[0] if row else None


def insert_scraped_page(website_id: int, page_url: str, page_type: str,
                         raw_content: str, status_code: int = 200) -> int:
    """
    Inserts a scraped page record.
    
    Returns:
        id of the inserted page
    """
    word_count = len(raw_content.split()) if raw_content else 0
    engine = get_engine()
    db_url = get_connection_string()
    is_sqlite = db_url.startswith("sqlite")
    
    with engine.begin() as conn:
        if is_sqlite:
            conn.execute(
                text("""
                    INSERT INTO scraped_pages (website_id, page_url, page_type, raw_content, status_code, word_count)
                    VALUES (:website_id, :page_url, :page_type, :raw_content, :status_code, :word_count)
                """),
                {
                    "website_id": website_id,
                    "page_url": page_url,
                    "page_type": page_type,
                    "raw_content": raw_content,
                    "status_code": status_code,
                    "word_count": word_count
                }
            )
            result = conn.execute(text("SELECT last_insert_rowid()"))
            val = result.fetchone()[0]
            # Perform commit
            return val
        else:
            result = conn.execute(
                text("""
                    INSERT INTO scraped_pages (website_id, page_url, page_type, raw_content, status_code, word_count)
                    VALUES (:website_id, :page_url, :page_type, :raw_content, :status_code, :word_count)
                    RETURNING id
                """),
                {
                    "website_id": website_id,
                    "page_url": page_url,
                    "page_type": page_type,
                    "raw_content": raw_content,
                    "status_code": status_code,
                    "word_count": word_count
                }
            )
            return result.fetchone()[0]


def insert_dark_pattern(page_id: int, website_id: int, pattern_type: str,
                         pattern_name: str, severity: str, evidence: str,
                         element_tag: str = None, confidence: float = 1.0) -> int:
    """
    Inserts a detected dark pattern record.
    """
    engine = get_engine()
    db_url = get_connection_string()
    is_sqlite = db_url.startswith("sqlite")
    
    with engine.begin() as conn:
        if is_sqlite:
            conn.execute(
                text("""
                    INSERT INTO dark_patterns 
                        (page_id, website_id, pattern_type, pattern_name, severity, evidence, element_tag, confidence)
                    VALUES 
                        (:page_id, :website_id, :pattern_type, :pattern_name, :severity, :evidence, :element_tag, :confidence)
                """),
                {
                    "page_id": page_id,
                    "website_id": website_id,
                    "pattern_type": pattern_type,
                    "pattern_name": pattern_name,
                    "severity": severity,
                    "evidence": evidence,
                    "element_tag": element_tag,
                    "confidence": confidence
                }
            )
            result = conn.execute(text("SELECT last_insert_rowid()"))
            val = result.fetchone()[0]
            return val
        else:
            result = conn.execute(
                text("""
                    INSERT INTO dark_patterns 
                        (page_id, website_id, pattern_type, pattern_name, severity, evidence, element_tag, confidence)
                    VALUES 
                        (:page_id, :website_id, :pattern_type, :pattern_name, :severity, :evidence, :element_tag, :confidence)
                    RETURNING id
                """),
                {
                    "page_id": page_id,
                    "website_id": website_id,
                    "pattern_type": pattern_type,
                    "pattern_name": pattern_name,
                    "severity": severity,
                    "evidence": evidence,
                    "element_tag": element_tag,
                    "confidence": confidence
                }
            )
            return result.fetchone()[0]


def insert_risk_score(website_id: int, dprs_score: float, total_pages: int,
                       total_patterns: int, high: int, medium: int, low: int) -> None:
    """
    Computes compliance status and inserts the DPRS score for a website.
    """
    if dprs_score <= 30:
        status = "COMPLIANT"
    elif dprs_score <= 60:
        status = "AT RISK"
    else:
        status = "NON-COMPLIANT"

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO risk_scores 
                    (website_id, dprs_score, total_pages_scanned, total_patterns,
                     high_severity, medium_severity, low_severity, compliance_status)
                VALUES 
                    (:website_id, :dprs_score, :total_pages, :total_patterns,
                     :high, :medium, :low, :status)
            """),
            {
                "website_id": website_id,
                "dprs_score": round(dprs_score, 2),
                "total_pages": total_pages,
                "total_patterns": total_patterns,
                "high": high,
                "medium": medium,
                "low": low,
                "status": status
            }
        )
    print(f"✅ Risk score saved: DPRS={dprs_score:.2f}, Status={status}")


from urllib.parse import urlparse


def save_live_scan_to_db(page_url: str, page_type: str, raw_content: str, 
                         status_code: int, detected_patterns: list, score_info: dict) -> int:
    """
    Saves a live scan result to the database with domain registration and URL deduplication.
    
    1. Extracts domain name and gets/creates website entry in `websites`.
    2. Checks if `page_url` already exists in `scraped_pages`.
       - If exists: updates existing page timestamp/content, deletes old patterns for this page.
       - If new: inserts new scraped page.
    3. Inserts detected dark patterns into `dark_patterns`.
    4. Computes updated site-wide DPRS and inserts into `risk_scores`.
    """
    parsed = urlparse(page_url)
    domain = parsed.netloc or parsed.path.split('/')[0]
    domain_clean = domain.replace("www.", "").split(".")[0].capitalize()
    if not domain_clean:
        domain_clean = "Custom Web Site"
    base_website_url = f"{parsed.scheme or 'https'}://{domain}"

    # 1. Get or create website
    website_id = insert_website(name=domain_clean, url=base_website_url)

    engine = get_engine()
    word_count = len(raw_content.split()) if raw_content else 0

    with engine.begin() as conn:
        # 2. Check for existing page URL (Deduplication)
        res = conn.execute(
            text("SELECT id FROM scraped_pages WHERE page_url = :url"),
            {"url": page_url}
        )
        row = res.fetchone()

        if row:
            page_id = row[0]
            # Update existing page details
            conn.execute(
                text("""
                    UPDATE scraped_pages
                    SET raw_content = :raw_content,
                        status_code = :status_code,
                        word_count = :word_count,
                        scraped_at = CURRENT_TIMESTAMP
                    WHERE id = :page_id
                """),
                {
                    "raw_content": raw_content,
                    "status_code": status_code,
                    "word_count": word_count,
                    "page_id": page_id
                }
            )
            # Remove old patterns for this page to prevent duplicates
            conn.execute(
                text("DELETE FROM dark_patterns WHERE page_id = :page_id"),
                {"page_id": page_id}
            )
        else:
            # Insert new page
            is_sqlite = get_connection_string().startswith("sqlite")
            if is_sqlite:
                conn.execute(
                    text("""
                        INSERT INTO scraped_pages (website_id, page_url, page_type, raw_content, status_code, word_count)
                        VALUES (:website_id, :page_url, :page_type, :raw_content, :status_code, :word_count)
                    """),
                    {
                        "website_id": website_id,
                        "page_url": page_url,
                        "page_type": page_type,
                        "raw_content": raw_content,
                        "status_code": status_code,
                        "word_count": word_count
                    }
                )
                res_id = conn.execute(text("SELECT last_insert_rowid()"))
                page_id = res_id.fetchone()[0]
            else:
                res_id = conn.execute(
                    text("""
                        INSERT INTO scraped_pages (website_id, page_url, page_type, raw_content, status_code, word_count)
                        VALUES (:website_id, :page_url, :page_type, :raw_content, :status_code, :word_count)
                        RETURNING id
                    """),
                    {
                        "website_id": website_id,
                        "page_url": page_url,
                        "page_type": page_type,
                        "raw_content": raw_content,
                        "status_code": status_code,
                        "word_count": word_count
                    }
                )
                page_id = res_id.fetchone()[0]

        # 3. Insert fresh detected patterns
        for p in detected_patterns:
            conn.execute(
                text("""
                    INSERT INTO dark_patterns 
                        (page_id, website_id, pattern_type, pattern_name, severity, evidence, element_tag, confidence)
                    VALUES 
                        (:page_id, :website_id, :pattern_type, :pattern_name, :severity, :evidence, :element_tag, :confidence)
                """),
                {
                    "page_id": page_id,
                    "website_id": website_id,
                    "pattern_type": p["pattern_type"],
                    "pattern_name": p["pattern_name"],
                    "severity": p["severity"],
                    "evidence": p["evidence"],
                    "element_tag": p.get("element_tag", "text"),
                    "confidence": p.get("confidence", 1.0)
                }
            )

        # 4. Insert/update risk score entry
        high_cnt = sum(1 for p in detected_patterns if p["severity"] == "HIGH")
        med_cnt  = sum(1 for p in detected_patterns if p["severity"] == "MEDIUM")
        low_cnt  = sum(1 for p in detected_patterns if p["severity"] == "LOW")

        status_val = score_info["compliance_status"]
        dprs_val   = score_info["dprs_score"]

        conn.execute(
            text("""
                INSERT INTO risk_scores 
                    (website_id, dprs_score, total_pages_scanned, total_patterns,
                     high_severity, medium_severity, low_severity, compliance_status)
                VALUES 
                    (:website_id, :dprs_score, 1, :total_patterns,
                     :high, :medium, :low, :status)
            """),
            {
                "website_id": website_id,
                "dprs_score": round(dprs_val, 2),
                "total_patterns": len(detected_patterns),
                "high": high_cnt,
                "medium": med_cnt,
                "low": low_cnt,
                "status": status_val
            }
        )

    print(f"✅ Saved live scan to DB: Website={domain_clean}, URL={page_url}, Patterns={len(detected_patterns)}")
    return page_id


def bulk_insert_patterns(patterns_df: pd.DataFrame) -> None:
    """
    Bulk inserts a DataFrame of dark patterns into the database.
    
    Expected columns:
        page_id, website_id, pattern_type, pattern_name, severity, evidence, confidence
    """
    engine = get_engine()
    patterns_df.to_sql("dark_patterns", engine, if_exists="append", index=False)
    print(f"✅ Bulk inserted {len(patterns_df)} dark patterns")


# ============================================================
# RETRIEVAL FUNCTIONS (for notebooks & dashboard)
# ============================================================

def get_all_websites() -> pd.DataFrame:
    return load_dataframe("SELECT * FROM websites WHERE is_active = TRUE ORDER BY name")


def get_risk_scores_summary() -> pd.DataFrame:
    return load_dataframe("""
        SELECT w.name, r.dprs_score, r.compliance_status, r.total_patterns,
               r.high_severity, r.medium_severity, r.low_severity, r.scan_date
        FROM risk_scores r
        JOIN websites w ON r.website_id = w.id
        ORDER BY r.scan_date DESC, r.dprs_score DESC
    """)


def get_pattern_breakdown() -> pd.DataFrame:
    return load_dataframe("SELECT * FROM vw_pattern_breakdown")


def get_daily_trend() -> pd.DataFrame:
    return load_dataframe("SELECT * FROM vw_daily_trend ORDER BY detection_date")


# ============================================================
# MAIN: Test the connection
# ============================================================
if __name__ == "__main__":
    print("Testing Neon PostgreSQL connection...")
    test_connection()
    
    print("\nFetching websites...")
    df = get_all_websites()
    print(df)
