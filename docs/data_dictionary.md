# 📖 Data Dictionary — Dark Pattern Intelligence System (DPIS)

## Table: `websites`
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Auto-increment primary key | 1 |
| name | VARCHAR | Website display name | "Amazon India" |
| url | TEXT | Base URL of website | "https://www.amazon.in" |
| category | VARCHAR | Business category | "E-Commerce" |
| country | VARCHAR | Country of operation | "India" |
| is_active | BOOLEAN | Whether actively being tracked | TRUE |
| created_at | TIMESTAMP | When record was created | 2025-01-15 10:00:00 |
| updated_at | TIMESTAMP | Last update timestamp | 2025-01-15 10:00:00 |

## Table: `scraped_pages`
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Auto-increment primary key | 101 |
| website_id | INT | FK → websites.id | 1 |
| page_url | TEXT | Full URL of scraped page | "https://amazon.in/s?k=mobile" |
| page_type | VARCHAR | Page category | "search" / "homepage" / "product" / "checkout" |
| scraped_at | TIMESTAMP | When page was scraped | 2025-01-15 11:30:00 |
| status_code | INT | HTTP response code | 200 |
| raw_content | TEXT | Cleaned text extracted from page | "Only 3 left in stock..." |
| word_count | INT | Total words on page | 1847 |

## Table: `dark_patterns`
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Auto-increment primary key | 501 |
| page_id | INT | FK → scraped_pages.id | 101 |
| website_id | INT | FK → websites.id | 1 |
| pattern_type | VARCHAR | Category type of pattern | "Urgency" / "Trick" / "Sneaking" |
| pattern_name | VARCHAR | Specific pattern name | "Fake Countdown Timer" |
| severity | VARCHAR | Risk level | "HIGH" / "MEDIUM" / "LOW" |
| evidence | TEXT | Actual text where pattern was found | "Offer ends in 02:30:00" |
| element_tag | VARCHAR | HTML element type | "div" / "span" / "text" |
| confidence | DECIMAL | Detection confidence (0–1) | 0.95 |
| detected_at | TIMESTAMP | When detected | 2025-01-15 11:31:05 |

## Table: `risk_scores`
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | INT | Auto-increment primary key | 201 |
| website_id | INT | FK → websites.id | 1 |
| dprs_score | DECIMAL | Dark Pattern Risk Score (0–100) | 78.5 |
| total_pages_scanned | INT | Pages analyzed in this scan | 18 |
| total_patterns | INT | Total dark patterns found | 9 |
| high_severity | INT | Count of HIGH severity patterns | 5 |
| medium_severity | INT | Count of MEDIUM severity patterns | 3 |
| low_severity | INT | Count of LOW severity patterns | 1 |
| compliance_status | VARCHAR | Overall compliance verdict | "NON-COMPLIANT" |
| scan_date | DATE | Date of the scan | 2025-01-15 |
| scored_at | TIMESTAMP | When score was calculated | 2025-01-15 12:00:00 |

---

## DPRS Score Formula

```
DPRS = (HIGH × 10 + MEDIUM × 5 + LOW × 2) / (Total_Patterns × 10) × 100

Score Ranges:
  0  – 30  →  COMPLIANT      (Green)
  31 – 60  →  AT RISK        (Orange)
  61 – 100 →  NON-COMPLIANT  (Red)
```

## Pattern Types Reference
| Pattern Type | Description |
|-------------|-------------|
| Urgency | Creates artificial time pressure |
| Trick | Deceives user into unintended action |
| Sneaking | Adds unwanted items/subscriptions |
| Misdirection | Directs attention away from key info |
| Obstruction | Makes desired actions difficult |
| Psychological | Exploits emotions and cognitive biases |
| Social | Misuses social proof or contacts |
