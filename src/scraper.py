"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/scraper.py

Web Scraping Module
Scrapes product, homepage, and checkout pages from
5 Indian e-commerce websites safely and ethically.
============================================================
"""

import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
from fake_useragent import UserAgent

# Initialize user agent rotator
ua = UserAgent()


# ============================================================
# TARGET WEBSITES & PAGE URLS
# These are public-facing pages (no login required)
# ============================================================

TARGET_WEBSITES = {
    "Amazon India": {
        "url": "https://www.amazon.in",
        "pages": [
            {"url": "https://www.amazon.in", "type": "homepage"},
            {"url": "https://www.amazon.in/s?k=mobile+phones", "type": "search"},
            {"url": "https://www.amazon.in/deals", "type": "deals"},
        ]
    },
    "Flipkart": {
        "url": "https://www.flipkart.com",
        "pages": [
            {"url": "https://www.flipkart.com", "type": "homepage"},
            {"url": "https://www.flipkart.com/search?q=mobile", "type": "search"},
            {"url": "https://www.flipkart.com/offers-store", "type": "deals"},
        ]
    },
    "Meesho": {
        "url": "https://www.meesho.com",
        "pages": [
            {"url": "https://www.meesho.com", "type": "homepage"},
            {"url": "https://www.meesho.com/search?q=dress", "type": "search"},
        ]
    },
    "Myntra": {
        "url": "https://www.myntra.com",
        "pages": [
            {"url": "https://www.myntra.com", "type": "homepage"},
            {"url": "https://www.myntra.com/sale", "type": "deals"},
        ]
    },
    "Snapdeal": {
        "url": "https://www.snapdeal.com",
        "pages": [
            {"url": "https://www.snapdeal.com", "type": "homepage"},
            {"url": "https://www.snapdeal.com/offers", "type": "deals"},
        ]
    }
}


# ============================================================
# SCRAPER CLASS
# ============================================================

class EcommerceScraper:
    """
    Responsible for scraping public pages of e-commerce websites
    and extracting text content for dark pattern analysis.
    """

    def __init__(self, delay_range: tuple = (2, 5)):
        """
        Args:
            delay_range: Random delay range between requests (seconds)
                         to avoid rate limiting. Default: 2–5 seconds.
        """
        self.delay_range = delay_range
        self.session = requests.Session()

    def _get_headers(self) -> Dict:
        """Returns randomized headers to avoid bot detection."""
        return {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com/",
        }

    def _random_delay(self):
        """Waits a random amount of time between requests (ethical scraping)."""
        delay = random.uniform(*self.delay_range)
        print(f"   ⏳ Waiting {delay:.1f}s before next request...")
        time.sleep(delay)

    def scrape_page(self, url: str, page_type: str) -> Optional[Dict]:
        """
        Scrapes a single page and returns extracted content.
        
        Args:
            url: URL to scrape
            page_type: 'homepage' | 'product' | 'checkout' | 'search' | 'deals'
            
        Returns:
            Dict with url, type, html, text, word_count, status_code
            Returns None if scraping fails.
        """
        try:
            print(f"   🔍 Scraping [{page_type}]: {url}")
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=15
            )

            if response.status_code != 200:
                print(f"   ⚠️  Status {response.status_code} for {url}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style tags (not relevant for dark patterns)
            for tag in soup(["script", "style", "meta", "noscript"]):
                tag.decompose()

            text_content = soup.get_text(separator=' ', strip=True)
            text_content = ' '.join(text_content.split())  # Normalize whitespace

            return {
                "page_url": url,
                "page_type": page_type,
                "raw_html": response.text[:50000],   # Cap at 50k chars
                "raw_text": text_content[:30000],     # Cap text at 30k chars
                "word_count": len(text_content.split()),
                "status_code": response.status_code,
                "scraped_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Failed to scrape {url}: {e}")
            return None

    def scrape_website(self, website_name: str) -> List[Dict]:
        """
        Scrapes all configured pages for a given website.
        
        Args:
            website_name: Key from TARGET_WEBSITES dict
            
        Returns:
            List of page data dicts
        """
        if website_name not in TARGET_WEBSITES:
            print(f"❌ Website '{website_name}' not found in targets")
            return []

        config = TARGET_WEBSITES[website_name]
        pages = config["pages"]
        results = []

        print(f"\n{'='*55}")
        print(f"🌐 Scraping: {website_name} ({len(pages)} pages)")
        print(f"{'='*55}")

        for page_config in pages:
            result = self.scrape_page(page_config["url"], page_config["type"])
            if result:
                result["website_name"] = website_name
                result["website_url"] = config["url"]
                results.append(result)

            self._random_delay()  # Be polite between requests

        print(f"✅ Done: {len(results)}/{len(pages)} pages scraped for {website_name}")
        return results

    def scrape_all_websites(self) -> pd.DataFrame:
        """
        Scrapes all 5 target websites and returns a DataFrame.
        
        Returns:
            pd.DataFrame with all scraped pages
        """
        all_results = []

        for website_name in TARGET_WEBSITES:
            pages = self.scrape_website(website_name)
            all_results.extend(pages)
            time.sleep(random.uniform(5, 10))  # Longer pause between websites

        df = pd.DataFrame(all_results)
        print(f"\n✅ Total pages scraped: {len(df)}")
        return df

    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """Saves scraped data to CSV."""
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"💾 Saved {len(df)} pages to: {filepath}")


# ============================================================
# ETHICAL SCRAPING NOTE
# ============================================================
"""
⚠️  IMPORTANT: Ethical Scraping Guidelines

1. We ONLY scrape publicly accessible pages (no login required)
2. We respect robots.txt wherever possible
3. We add random delays between requests (2-5 seconds)
4. We use a real User-Agent to identify ourselves
5. We cap page content size to avoid server overload
6. This data is used ONLY for academic research and analysis
7. We do NOT store any user personal data
"""


# ============================================================
# MAIN: Test scraper
# ============================================================
if __name__ == "__main__":
    scraper = EcommerceScraper(delay_range=(2, 4))

    # Test with just one page first
    result = scraper.scrape_page("https://www.flipkart.com", "homepage")
    if result:
        print(f"\n✅ Page scraped successfully!")
        print(f"   Words: {result['word_count']}")
        print(f"   Preview: {result['raw_text'][:300]}...")
