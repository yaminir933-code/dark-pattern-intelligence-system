"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/classifier.py

Dark Pattern Detection & Classification Engine
Detects 12 categories of dark patterns using:
  - Rule-based keyword matching
  - Regex pattern matching
  - HTML element analysis
  - Confidence scoring
============================================================
"""

import re
import nltk
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)


# ============================================================
# DARK PATTERN DEFINITIONS
# 12 categories with keywords, patterns, and severity
# ============================================================

DARK_PATTERN_RULES = {

    "Fake Countdown Timer": {
        "type": "Urgency",
        "severity": "HIGH",
        "keywords": [
            "offer ends in", "deal expires", "limited time", "expires in",
            "only today", "ends tonight", "flash sale ends", "hurry",
            "countdown", "time running out", "don't miss out", "ending soon"
        ],
        "regex_patterns": [
            r'\d{2}:\d{2}:\d{2}',                    # HH:MM:SS timer
            r'\d+\s*(hours?|hrs?|minutes?|mins?|seconds?)\s*left',
            r'(sale|offer|deal)\s+ends?\s+in\s+\d+'
        ],
        "html_tags": ["timer", "countdown"],
        "html_classes": ["countdown", "timer", "sale-timer", "offer-timer"]
    },

    "Hidden Subscription": {
        "type": "Trick",
        "severity": "HIGH",
        "keywords": [
            "auto-renew", "auto renew", "recurring charge", "subscription",
            "billed annually", "billed monthly", "cancel anytime",
            "free trial then", "after trial period", "membership fee",
            "charged automatically"
        ],
        "regex_patterns": [
            r'(charged?|billed?)\s+(automatically|every\s+month|annually)',
            r'after\s+(free\s+)?trial',
            r'\$\d+\.?\d*\s*/\s*(month|year|mo|yr)'
        ],
        "html_tags": [],
        "html_classes": ["subscription-note", "recurring", "auto-renew"]
    },

    "Pre-checked Boxes": {
        "type": "Sneaking",
        "severity": "HIGH",
        "keywords": [
            "yes, add", "yes, sign me up", "yes, keep me informed",
            "add purchase protection", "add warranty", "include",
            "receive offers", "marketing emails"
        ],
        "regex_patterns": [
            r'checked.*?(newsletter|offers?|subscription|protection)',
            r'(add|include)\s+\w+\s+for\s+(free|\$\d+)',
        ],
        "html_tags": ["input"],
        "html_classes": ["pre-checked", "default-checked", "auto-selected"]
    },

    "Fake Scarcity": {
        "type": "Urgency",
        "severity": "MEDIUM",
        "keywords": [
            "only", "left in stock", "selling fast", "almost gone",
            "limited stock", "few left", "last one", "nearly sold out",
            "high demand", "people are viewing", "others are watching",
            "X people have this in their cart"
        ],
        "regex_patterns": [
            r'only\s+\d+\s+(left|remaining|in\s+stock)',
            r'\d+\s+people\s+(are\s+)?(viewing|watching|have\s+this)',
            r'(selling|going)\s+fast',
        ],
        "html_tags": [],
        "html_classes": ["stock-warning", "scarcity", "urgency-badge"]
    },

    "Price Drip": {
        "type": "Misdirection",
        "severity": "HIGH",
        "keywords": [
            "convenience fee", "service fee", "processing fee",
            "handling fee", "booking fee", "platform fee",
            "taxes and fees", "additional charges", "extra charges",
            "resort fee", "facility fee"
        ],
        "regex_patterns": [
            r'(convenience|service|processing|handling|platform)\s+fee',
            r'\+\s*\$\d+\.?\d*\s*(fee|charge|tax)',
            r'additional\s+(charges?|fees?)\s+apply'
        ],
        "html_tags": [],
        "html_classes": ["fee-notice", "extra-charge", "surcharge"]
    },

    "Roach Motel": {
        "type": "Obstruction",
        "severity": "HIGH",
        "keywords": [
            "to cancel", "call us to cancel", "cancel by phone",
            "cancellation policy", "difficult to cancel", "unsubscribe",
            "contact support to cancel", "no online cancellation"
        ],
        "regex_patterns": [
            r'cancel\s+(by\s+)?(calling?|phone|email|writing)',
            r'to\s+cancel.*?contact',
        ],
        "html_tags": [],
        "html_classes": ["cancel-info", "cancellation-note"]
    },

    "Confirm Shaming": {
        "type": "Psychological",
        "severity": "MEDIUM",
        "keywords": [
            "no thanks, i don't want", "no thanks, i hate saving",
            "no thanks, i prefer paying more", "i don't want deals",
            "no, i don't want to save", "i'll pass", "no thanks, i hate discounts",
            "decline", "i don't want to be informed"
        ],
        "regex_patterns": [
            r"no[,\s]+thanks?[,\s]+i\s+(don't|hate|prefer|dislike)",
            r"i\s+don't\s+want\s+(to\s+)?(save|deals?|discounts?|offers?)"
        ],
        "html_tags": [],
        "html_classes": ["shame-option", "negative-cta", "decline-btn"]
    },

    "Disguised Ads": {
        "type": "Misdirection",
        "severity": "MEDIUM",
        "keywords": [
            "sponsored", "promoted", "featured listing", "ad",
            "paid placement", "advertisement", "partner content"
        ],
        "regex_patterns": [
            r'\bsponsored\b',
            r'\bpromoted\b',
            r'\bad\b'
        ],
        "html_tags": [],
        "html_classes": ["sponsored", "ad-badge", "promoted-listing"]
    },

    "Friend Spam": {
        "type": "Social",
        "severity": "MEDIUM",
        "keywords": [
            "invite your friends", "share your contacts",
            "import contacts", "allow access to contacts",
            "invite friends to earn", "refer a friend"
        ],
        "regex_patterns": [
            r'import\s+(your\s+)?contacts',
            r'invite\s+(your\s+)?friends',
            r'share\s+with\s+contacts'
        ],
        "html_tags": [],
        "html_classes": ["referral", "invite-friends", "contact-import"]
    },

    "Misleading Free Trial": {
        "type": "Trick",
        "severity": "HIGH",
        "keywords": [
            "free trial", "start your free trial", "free for",
            "no credit card required", "cancel before", "trial period",
            "first month free", "try free"
        ],
        "regex_patterns": [
            r'free\s+(trial|for\s+\d+\s+(days?|months?))',
            r'cancel\s+before\s+\d+\s+(days?|months?)',
            r'(first|your\s+first)\s+(month|year)\s+free'
        ],
        "html_tags": [],
        "html_classes": ["free-trial", "trial-cta"]
    },

    "Price Comparison Prevention": {
        "type": "Misdirection",
        "severity": "LOW",
        "keywords": [
            "price match", "we'll match", "lowest price guarantee",
            "beat any price", "exclusive price", "member price only",
            "login to see price"
        ],
        "regex_patterns": [
            r'log\s*in\s+to\s+(see|view)\s+price',
            r'exclusive\s+(member|subscriber)\s+price',
        ],
        "html_tags": [],
        "html_classes": ["hidden-price", "login-for-price", "member-only-price"]
    },

    "Bait and Switch": {
        "type": "Misdirection",
        "severity": "HIGH",
        "keywords": [
            "out of stock", "no longer available", "similar product",
            "upgrade recommended", "better option available",
            "this item is unavailable", "try this instead"
        ],
        "regex_patterns": [
            r'(out\s+of\s+stock|no\s+longer\s+available)',
            r'(try|consider|see)\s+(this|similar|other|our)',
        ],
        "html_tags": [],
        "html_classes": ["out-of-stock", "unavailable", "alternative-product"]
    }
}


# ============================================================
# DPRS SCORE WEIGHTS
# ============================================================
SEVERITY_WEIGHTS = {
    "HIGH":   10,
    "MEDIUM":  5,
    "LOW":     2
}


# ============================================================
# CLASSIFIER ENGINE
# ============================================================

class DarkPatternClassifier:
    """
    Detects dark patterns in web page content using rule-based NLP.
    """

    def __init__(self):
        self.rules = DARK_PATTERN_RULES

    def classify_text(self, text: str, page_url: str = "") -> List[Dict[str, Any]]:
        """
        Analyzes plain text for dark patterns.
        
        Args:
            text: Plain text content of the page
            page_url: URL of the page (for reference)
            
        Returns:
            List of detected dark patterns with details
        """
        detected = []
        text_lower = text.lower()

        for pattern_name, rule in self.rules.items():
            # Check keywords
            for keyword in rule["keywords"]:
                if keyword.lower() in text_lower:
                    # Find the evidence (surrounding context)
                    idx = text_lower.find(keyword.lower())
                    evidence = text[max(0, idx-50): min(len(text), idx+100)].strip()

                    detected.append({
                        "pattern_name": pattern_name,
                        "pattern_type": rule["type"],
                        "severity": rule["severity"],
                        "evidence": evidence,
                        "element_tag": "text",
                        "confidence": 0.85,
                        "match_source": "keyword"
                    })
                    break  # One match per keyword per pattern is enough

            # Check regex patterns
            for regex in rule.get("regex_patterns", []):
                match = re.search(regex, text_lower, re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 60)
                    evidence = text[start:end].strip()

                    detected.append({
                        "pattern_name": pattern_name,
                        "pattern_type": rule["type"],
                        "severity": rule["severity"],
                        "evidence": evidence,
                        "element_tag": "text",
                        "confidence": 0.92,
                        "match_source": "regex"
                    })
                    break

        return detected

    def classify_html(self, html: str, page_url: str = "") -> List[Dict[str, Any]]:
        """
        Analyzes full HTML content for dark patterns.
        Checks both text content AND HTML attributes/classes.
        
        Args:
            html: Raw HTML content of the page
            
        Returns:
            List of detected dark patterns with details
        """
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # First run text-based classification
        detected = self.classify_text(text, page_url)

        # Then check HTML-specific patterns (classes, attributes)
        for pattern_name, rule in self.rules.items():
            for css_class in rule.get("html_classes", []):
                elements = soup.find_all(class_=re.compile(css_class, re.I))
                for el in elements:
                    detected.append({
                        "pattern_name": pattern_name,
                        "pattern_type": rule["type"],
                        "severity": rule["severity"],
                        "evidence": str(el)[:200],
                        "element_tag": el.name,
                        "confidence": 0.95,
                        "match_source": "html_class"
                    })

        # Remove duplicates by pattern_name
        seen = set()
        unique_detected = []
        for d in detected:
            if d["pattern_name"] not in seen:
                seen.add(d["pattern_name"])
                unique_detected.append(d)

        return unique_detected

    def compute_dprs(self, detected_patterns: List[Dict]) -> Dict:
        """
        Computes the Dark Pattern Risk Score (DPRS) for a website/page.
        
        Formula:
            DPRS = (HIGH×10 + MEDIUM×5 + LOW×2) / (total_patterns × 10) × 100
            
        Returns:
            Dict with dprs_score, compliance_status, counts
        """
        high   = sum(1 for p in detected_patterns if p["severity"] == "HIGH")
        medium = sum(1 for p in detected_patterns if p["severity"] == "MEDIUM")
        low    = sum(1 for p in detected_patterns if p["severity"] == "LOW")
        total  = len(detected_patterns)

        if total == 0:
            return {
                "dprs_score": 0.0,
                "compliance_status": "COMPLIANT",
                "total_patterns": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0
            }

        weighted_score = (high * 10 + medium * 5 + low * 2)
        max_possible   = total * 10
        dprs = round((weighted_score / max_possible) * 100, 2)

        if dprs <= 30:
            status = "COMPLIANT"
        elif dprs <= 60:
            status = "AT RISK"
        else:
            status = "NON-COMPLIANT"

        return {
            "dprs_score": dprs,
            "compliance_status": status,
            "total_patterns": total,
            "high_severity": high,
            "medium_severity": medium,
            "low_severity": low
        }


# ============================================================
# QUICK TEST
# ============================================================
if __name__ == "__main__":
    classifier = DarkPatternClassifier()

    # Test with sample text
    sample_text = """
    Hurry! Only 3 left in stock! 
    Offer ends in 02:30:00. 
    ✅ Yes, add purchase protection for ₹199 (pre-checked)
    Auto-renews at ₹499/month. Cancel before 30 days.
    No thanks, I don't want to save money.
    """

    results = classifier.classify_text(sample_text, "https://test-site.com")
    score = classifier.compute_dprs(results)

    print(f"\n{'='*50}")
    print(f"DARK PATTERNS DETECTED: {len(results)}")
    print(f"{'='*50}")
    for r in results:
        print(f"  [{r['severity']}] {r['pattern_name']}")
        print(f"         → Evidence: {r['evidence'][:80]}...")

    print(f"\nDPRS SCORE: {score['dprs_score']}")
    print(f"STATUS: {score['compliance_status']}")
