"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/run_pipeline.py

End-to-End Execution Pipeline:
1. Initialize the database (SQLite / PostgreSQL)
2. Scrape target websites ethically
3. Classify scraped page contents for dark patterns
4. Compute DPRS and save all results to the database
5. Export clean datasets to CSV for EDA
6. Generate Excel reports
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

import argparse
import pandas as pd
from datetime import datetime

# Resolve project paths
src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_dir)
sys.path.append(project_root)

from src.db_connector import (
    init_db, test_connection, get_all_websites, 
    insert_scraped_page, insert_dark_pattern, 
    insert_risk_score, load_dataframe
)
from src.scraper import EcommerceScraper, TARGET_WEBSITES
from src.classifier import DarkPatternClassifier
from src.report_generator import (
    create_audit_template, create_scores_report, create_kpi_tracker
)

def run_database_init(force=False):
    """Initializes the database connection and tables."""
    print("\n⚙️  Initializing database...")
    init_db(force=force)
    test_connection()

def run_pipeline(init_db_flag=False, force_init=False, limit_pages=None):
    """Runs the entire end-to-end data pipeline."""
    print("🚀 Starting DPIS End-to-End Pipeline")
    print(f"📅 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Initialize Database if requested
    if init_db_flag or force_init:
        run_database_init(force=force_init)
    
    # Verify DB connection works
    if not test_connection():
        print("❌ Cannot proceed: database connection failed.")
        return False

    # Get target websites mapping
    websites_df = get_all_websites()
    if len(websites_df) == 0:
        # DB might not be initialized, try initializing
        run_database_init(force=False)
        websites_df = get_all_websites()
        if len(websites_df) == 0:
            print("❌ No websites found in the database. Please initialize the DB first.")
            return False

    website_id_map = {row['name']: row['id'] for _, row in websites_df.iterrows()}
    print(f"📋 Targets: {list(website_id_map.keys())}")

    # Step 2: Initialize Scraper & Classifier
    scraper = EcommerceScraper(delay_range=(1, 3))  # slightly faster delays for execution
    classifier = DarkPatternClassifier()

    all_detected_patterns = []
    scraped_pages_count = 0
    patterns_count = 0

    print("\n🕷️  Step 1: Scraping and Analyzing Pages...")
    for website_name, config in TARGET_WEBSITES.items():
        website_id = website_id_map.get(website_name)
        if not website_id:
            print(f"⚠️  Website {website_name} not found in DB table, skipping...")
            continue
            
        print(f"\n🌐 Scanning: {website_name}...")
        pages_to_scan = config["pages"]
        if limit_pages:
            pages_to_scan = pages_to_scan[:limit_pages]

        site_patterns = []
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0
        total_site_pages = 0

        for page_config in pages_to_scan:
            # Scrape page
            scraped_data = scraper.scrape_page(page_config["url"], page_config["type"])
            if not scraped_data:
                continue

            total_site_pages += 1
            scraped_pages_count += 1

            # Insert page into database
            page_id = insert_scraped_page(
                website_id=website_id,
                page_url=scraped_data["page_url"],
                page_type=scraped_data["page_type"],
                raw_content=scraped_data["raw_text"],
                status_code=scraped_data["status_code"]
            )

            # Classify content for dark patterns
            # Check both HTML elements and raw text
            detected = classifier.classify_html(scraped_data["raw_html"], scraped_data["page_url"])
            
            # Save detected patterns to database
            for p in detected:
                insert_dark_pattern(
                    page_id=page_id,
                    website_id=website_id,
                    pattern_type=p["pattern_type"],
                    pattern_name=p["pattern_name"],
                    severity=p["severity"],
                    evidence=p["evidence"],
                    element_tag=p["element_tag"],
                    confidence=p["confidence"]
                )
                
                # Keep in memory for scoring & dataset export
                p["website_name"] = website_name
                p["page_url"] = scraped_data["page_url"]
                p["page_type"] = scraped_data["page_type"]
                site_patterns.append(p)
                all_detected_patterns.append(p)
                patterns_count += 1

                if p["severity"] == "HIGH":
                    high_cnt += 1
                elif p["severity"] == "MEDIUM":
                    med_cnt += 1
                elif p["severity"] == "LOW":
                    low_cnt += 1

            # Ethical sleep
            scraper._random_delay()

        # Step 3: Compute & Save Risk Score for this website
        dprs_info = classifier.compute_dprs(site_patterns)
        insert_risk_score(
            website_id=website_id,
            dprs_score=dprs_info["dprs_score"],
            total_pages=total_site_pages,
            total_patterns=len(site_patterns),
            high=high_cnt,
            medium=med_cnt,
            low=low_cnt
        )

    print(f"\n📊 Scanning Complete! Scraped {scraped_pages_count} pages, found {patterns_count} dark patterns.")

    # Step 4: Export clean dataset to CSV for EDA & Dashboard compatibility
    print("\n💾 Step 2: Exporting Clean Datasets...")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Save the patterns dataframe
    if all_detected_patterns:
        patterns_df = pd.DataFrame(all_detected_patterns)
    else:
        # fallback to empty dataframe with correct columns
        patterns_df = pd.DataFrame(columns=[
            "website_name", "page_url", "page_type", "pattern_name", 
            "pattern_type", "severity", "evidence", "confidence"
        ])
        
    patterns_csv_path = os.path.join(processed_dir, "detected_patterns.csv")
    patterns_df.to_csv(patterns_csv_path, index=False, encoding='utf-8')
    print(f"   Saved clean patterns dataset to: {patterns_csv_path}")

    # Step 5: Generate Excel Reports
    print("\n📊 Step 3: Generating Excel Reports...")
    excel_dir = os.path.join(project_root, "data", "excel")
    os.makedirs(excel_dir, exist_ok=True)

    # 1. Generate manual audit template
    create_audit_template(os.path.join(excel_dir, "dark_pattern_audit_template.xlsx"))
    
    # 2. Fetch risk scores from DB to build the website_scores sheet
    scores_summary_df = load_dataframe("""
        SELECT w.name AS website, r.dprs_score, r.compliance_status,
               r.total_patterns, r.high_severity AS high, r.medium_severity AS medium,
               r.low_severity AS low, r.scan_date
        FROM risk_scores r
        JOIN websites w ON r.website_id = w.id
        WHERE r.scan_date = (SELECT MAX(scan_date) FROM risk_scores WHERE website_id = r.website_id)
    """)
    scores_list = scores_summary_df.to_dict('records')
    create_scores_report(scores_list, os.path.join(excel_dir, "website_scores.xlsx"))

    # 3. Generate KPI tracker
    create_kpi_tracker(os.path.join(excel_dir, "kpi_tracker.xlsx"))

    print("\n🎉 Pipeline Execution Complete!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the DPIS End-to-End Data Pipeline")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database schema")
    parser.add_argument("--force-init", action="store_true", help="Force recreate database schema (drops all tables)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pages scraped per website (for quick testing)")
    
    args = parser.parse_args()
    
    run_pipeline(
        init_db_flag=args.init_db,
        force_init=args.force_init,
        limit_pages=args.limit
    )
