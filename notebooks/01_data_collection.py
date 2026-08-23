"""
============================================================
NOTEBOOK 01: Data Collection
Dark Pattern Intelligence System (DPIS)

Run this notebook first to scrape data from all 5 websites
and save raw results to CSV and PostgreSQL.
============================================================
"""

# ── Cell 1: Install & Import Libraries ──────────────────────
# %pip install requests beautifulsoup4 fake-useragent psycopg2-binary sqlalchemy python-dotenv tqdm

import sys
import os
sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm

from src.scraper import EcommerceScraper, TARGET_WEBSITES
from src.db_connector import (
    test_connection, get_all_websites, insert_scraped_page
)

print("✅ Libraries loaded successfully!")
print(f"📅 Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ── Cell 2: Test Database Connection ────────────────────────
print("\n🔌 Testing Neon PostgreSQL connection...")
is_connected = test_connection()

if is_connected:
    websites_df = get_all_websites()
    print(f"\n📋 Websites in database: {len(websites_df)}")
    print(websites_df[['id', 'name', 'url']].to_string(index=False))
else:
    print("❌ Please check your .env file and Neon credentials")


# ── Cell 3: Initialize Scraper ───────────────────────────────
scraper = EcommerceScraper(delay_range=(2, 5))

# Test with one page first
print("\n🧪 Quick test: Scraping Flipkart homepage...")
test_page = scraper.scrape_page("https://www.flipkart.com", "homepage")

if test_page:
    print(f"✅ Test successful!")
    print(f"   Word count: {test_page['word_count']}")
    print(f"   Preview: {test_page['raw_text'][:200]}...")
else:
    print("❌ Test failed — check your internet connection")


# ── Cell 4: Scrape All Websites ──────────────────────────────
print("\n🚀 Starting full scrape of all 5 websites...")
print("⏳ This will take 5–10 minutes (ethical delays included)")

all_pages = scraper.scrape_all_websites()

print(f"\n{'='*50}")
print(f"✅ SCRAPING COMPLETE")
print(f"   Total pages scraped: {len(all_pages)}")
print(f"   Columns: {list(all_pages.columns)}")
print(all_pages[['website_name', 'page_type', 'word_count', 'status_code']].to_string(index=False))


# ── Cell 5: Save Raw Data to CSV ─────────────────────────────
os.makedirs('../data/raw', exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
raw_csv_path = f"../data/raw/scraped_pages_{timestamp}.csv"

# Save everything except full HTML (too large)
save_df = all_pages.drop(columns=['raw_html'], errors='ignore')
save_df.to_csv(raw_csv_path, index=False, encoding='utf-8')

print(f"\n💾 Raw data saved to: {raw_csv_path}")
print(f"   Shape: {save_df.shape}")


# ── Cell 6: Load to PostgreSQL ───────────────────────────────
print("\n📤 Loading scraped pages to Neon PostgreSQL...")

# Map website names to database IDs
website_id_map = {
    "Amazon India": 1,
    "Flipkart":     2,
    "Meesho":       3,
    "Myntra":       4,
    "Snapdeal":     5
}

inserted_count = 0
for _, row in tqdm(all_pages.iterrows(), total=len(all_pages), desc="Inserting pages"):
    website_id = website_id_map.get(row['website_name'])
    if website_id:
        page_id = insert_scraped_page(
            website_id=website_id,
            page_url=row['page_url'],
            page_type=row['page_type'],
            raw_content=row.get('raw_text', ''),
            status_code=row.get('status_code', 200)
        )
        if page_id:
            inserted_count += 1

print(f"\n✅ Inserted {inserted_count} pages into PostgreSQL")
print(f"🎉 Data Collection Complete! Proceed to Notebook 02.")
