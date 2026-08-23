"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/db_connector.py

PostgreSQL (Neon) Database Connection Module
============================================================
"""

import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection_string() -> str:
    """Returns the Neon PostgreSQL connection string from .env"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Build from individual parts
        host     = os.getenv("DB_HOST")
        port     = os.getenv("DB_PORT", "5432")
        dbname   = os.getenv("DB_NAME")
        user     = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        sslmode  = os.getenv("DB_SSLMODE", "require")
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"
    return db_url


def get_engine():
    """Creates and returns a SQLAlchemy engine for Neon PostgreSQL"""
    connection_string = get_connection_string()
    engine = create_engine(connection_string)
    return engine


def get_psycopg2_connection():
    """Creates and returns a raw psycopg2 connection"""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )
    return conn


def test_connection() -> bool:
    """Tests the database connection — returns True if successful"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Neon PostgreSQL connection successful!")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


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
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                INSERT INTO websites (name, url, category, country)
                VALUES (:name, :url, :category, :country)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
            """),
            {"name": name, "url": url, "category": category, "country": country}
        )
        conn.commit()
        row = result.fetchone()
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
    with engine.connect() as conn:
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
        conn.commit()
        return result.fetchone()[0]


def insert_dark_pattern(page_id: int, website_id: int, pattern_type: str,
                         pattern_name: str, severity: str, evidence: str,
                         element_tag: str = None, confidence: float = 1.0) -> int:
    """
    Inserts a detected dark pattern record.
    
    Args:
        severity: 'HIGH' | 'MEDIUM' | 'LOW'
        confidence: float between 0.0 and 1.0
    
    Returns:
        id of the inserted record
    """
    engine = get_engine()
    with engine.connect() as conn:
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
        conn.commit()
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
    with engine.connect() as conn:
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
        conn.commit()
    print(f"✅ Risk score saved: DPRS={dprs_score:.2f}, Status={status}")


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
