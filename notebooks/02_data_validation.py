"""
============================================================
NOTEBOOK 02: Data Validation and Quality Assurance
Dark Pattern Intelligence System (DPIS)

This notebook implements enterprise-grade data validation,
quality checks, data cleaning, and statistical outlier detection.
Skills Demonstrated:
  - Data Validation and Integrity Checks (Nulls, Duplicates, Types)
  - Data Cleaning and Preprocessing (Standardization, Imputation)
  - Outlier Detection using Interquartile Range (IQR) and Z-Score
  - Before vs After Quality Audit Reporting
============================================================
"""

import os
import sys
sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 65)
print("DPIS NOTEBOOK 02: DATA VALIDATION & QUALITY AUDIT")
print("=" * 65)

# --- Step 1: Load Data ---
raw_path = '../data/processed/detected_patterns.csv'
if not os.path.exists(raw_path):
    print("Note: Using sample reference data for validation demonstration")
    df = pd.DataFrame({
        'pattern_name': ['Disguised Ads', 'Fake Scarcity', 'Disguised Ads', 'Urgency Countdown', 'Forced Action', None],
        'pattern_type': ['Misdirection', 'Urgency', 'Misdirection', 'Scarcity', 'Obstruction', 'Unknown'],
        'severity': ['MEDIUM', 'HIGH', 'MEDIUM', 'HIGH', 'LOW', 'MEDIUM'],
        'evidence': ['Requires JavaScript', 'Only 2 items left in stock!', 'SnapDeal 404 page', 'Hurry, sale ends in 02:00', 'Pre-checked insurance box', ''],
        'element_tag': ['text', 'button', 'text', 'div', 'input', 'span'],
        'confidence': [0.85, 0.92, 0.85, 0.98, 0.75, 0.40],
        'match_source': ['keyword', 'rule', 'keyword', 'nlp_model', 'rule', 'unknown'],
        'website_name': ['Amazon India', 'Flipkart', 'Snapdeal', 'Meesho', 'Myntra', 'Flipkart'],
        'page_url': ['https://www.amazon.in', 'https://www.flipkart.com', 'https://www.snapdeal.com/offers', 'https://www.meesho.com', 'https://www.myntra.com', 'https://www.flipkart.com'],
        'page_type': ['homepage', 'product', 'deals', 'checkout', 'cart', 'homepage']
    })
else:
    df = pd.read_csv(raw_path)
    print(f"Loaded raw dataset from {raw_path}: {df.shape[0]} rows, {df.shape[1]} columns")

initial_rows = len(df)

# --- Step 2: Data Quality Assessment (Before Cleaning) ---
print("\n[1] DATA QUALITY AUDIT (INITIAL STATE)")
print("-" * 50)

missing_counts = df.isnull().sum()
missing_pct = (missing_counts / len(df)) * 100
quality_profile = pd.DataFrame({
    'Column': df.columns,
    'Data_Type': [str(df[col].dtype) for col in df.columns],
    'Missing_Values': missing_counts.values,
    'Missing_Percentage': missing_pct.round(2).values,
    'Unique_Values': [df[col].nunique() for col in df.columns]
})
print(quality_profile.to_string(index=False))

duplicates_count = df.duplicated().sum()
print(f"\nDuplicate rows detected: {duplicates_count}")

# --- Step 3: Data Cleaning & Preprocessing ---
print("\n[2] DATA CLEANING & STANDARDIZATION")
print("-" * 50)

cleaned_df = df.copy()

# A. Standardize string columns
str_cols = ['pattern_name', 'pattern_type', 'website_name', 'page_type']
for col in str_cols:
    if col in cleaned_df.columns:
        cleaned_df[col] = cleaned_df[col].astype(str).str.strip().str.title()

# B. Standardize Severity to UPPERCASE
if 'severity' in cleaned_df.columns:
    cleaned_df['severity'] = cleaned_df['severity'].astype(str).str.strip().str.upper()
    valid_severities = {'HIGH', 'MEDIUM', 'LOW'}
    cleaned_df['severity'] = cleaned_df['severity'].apply(lambda x: x if x in valid_severities else 'MEDIUM')

# C. Handle missing evidence & confidence
if 'evidence' in cleaned_df.columns:
    cleaned_df['evidence'] = cleaned_df['evidence'].fillna('No textual evidence captured').astype(str).str.strip()

if 'confidence' in cleaned_df.columns:
    cleaned_df['confidence'] = pd.to_numeric(cleaned_df['confidence'], errors='coerce')
    cleaned_df['confidence'] = cleaned_df['confidence'].fillna(cleaned_df['confidence'].median())
    # Clip between 0.0 and 1.0
    cleaned_df['confidence'] = cleaned_df['confidence'].clip(lower=0.0, upper=1.0)

# D. Remove duplicate records
cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
cleaned_rows = len(cleaned_df)
print(f"Rows before cleaning: {initial_rows} | Rows after deduplication: {cleaned_rows}")
print("Severity values standardized to: [HIGH, MEDIUM, LOW]")
print("Confidence scores normalized to interval [0.0, 1.0]")

# --- Step 4: Statistical Outlier Detection (IQR Method) ---
print("\n[3] STATISTICAL OUTLIER DETECTION (IQR METHOD)")
print("-" * 50)

q1 = cleaned_df['confidence'].quantile(0.25)
q3 = cleaned_df['confidence'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outliers = cleaned_df[(cleaned_df['confidence'] < lower_bound) | (cleaned_df['confidence'] > upper_bound)]
print(f"Confidence Q1: {q1:.3f} | Q3: {q3:.3f} | IQR: {iqr:.3f}")
print(f"Normal Range (Tukey's Fences): [{lower_bound:.3f}, {upper_bound:.3f}]")
print(f"Number of statistical outliers identified: {len(outliers)}")

if len(outliers) > 0:
    print("Outlier sample:")
    print(outliers[['website_name', 'pattern_name', 'confidence']].to_string(index=False))

# --- Step 5: Business Logic Validation Rules ---
print("\n[4] BUSINESS LOGIC VALIDATION RULES")
print("-" * 50)

rules_results = []

r1_pass = (cleaned_df['confidence'] >= 0.50).sum()
r1_fail = (cleaned_df['confidence'] < 0.50).sum()
rules_results.append({'Rule_ID': 'BR01', 'Description': 'Confidence Score >= 0.50', 'Passed': int(r1_pass), 'Failed': int(r1_fail), 'Status': 'PASS' if r1_fail == 0 else 'WARNING'})

r2_pass = cleaned_df['page_url'].str.startswith(('http://', 'https://')).sum() if 'page_url' in cleaned_df.columns else cleaned_rows
r2_fail = cleaned_rows - r2_pass
rules_results.append({'Rule_ID': 'BR02', 'Description': 'Valid HTTP/HTTPS URL Scheme', 'Passed': int(r2_pass), 'Failed': int(r2_fail), 'Status': 'PASS' if r2_fail == 0 else 'FAIL'})

r3_pass = cleaned_df['severity'].isin(['HIGH', 'MEDIUM', 'LOW']).sum()
r3_fail = cleaned_rows - r3_pass
rules_results.append({'Rule_ID': 'BR03', 'Description': 'Standardized Severity Level', 'Passed': int(r3_pass), 'Failed': int(r3_fail), 'Status': 'PASS' if r3_fail == 0 else 'FAIL'})

rules_df = pd.DataFrame(rules_results)
print(rules_df.to_string(index=False))

# --- Step 6: Export Cleaned Data and QA Audit Summary ---
os.makedirs('../data/processed', exist_ok=True)
audit_path = '../data/processed/data_quality_report.csv'
cleaned_path = '../data/processed/cleaned_patterns.csv'

quality_profile.to_csv(audit_path, index=False)
cleaned_df.to_csv(cleaned_path, index=False)

print("\n" + "=" * 65)
print(f"Data Quality Audit Report saved: {audit_path}")
print(f"Cleaned Data Export saved:       {cleaned_path}")
print("Data Validation Step Complete! Ready for EDA & SQL Analysis.")
print("=" * 65)
