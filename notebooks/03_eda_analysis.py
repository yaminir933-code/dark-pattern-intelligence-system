"""
============================================================
NOTEBOOK 03: Exploratory Data Analysis (EDA)
Dark Pattern Intelligence System (DPIS)

Deep-dive EDA on detected dark patterns:
  - Pattern frequency by website
  - Severity distribution
  - Page type analysis
  - Statistical tests
  - Word clouds
  - Correlation heatmaps
============================================================
"""

# ── Cell 1: Imports ──────────────────────────────────────────
import sys
sys.path.append('..')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from src.db_connector import load_dataframe, get_pattern_breakdown, get_risk_scores_summary

# Style settings
plt.style.use('seaborn-v0_8-darkgrid')
PALETTE = ['#C0392B', '#E67E22', '#27AE60', '#2980B9', '#8E44AD']
print("✅ EDA libraries loaded!")


# ── Cell 2: Load Data from PostgreSQL ───────────────────────
print("\n📥 Loading data from Neon PostgreSQL...")

# Load all detected dark patterns
patterns_df = load_dataframe("""
    SELECT dp.*, w.name AS website_name
    FROM dark_patterns dp
    JOIN websites w ON dp.website_id = w.id
    ORDER BY dp.detected_at DESC
""")

# Load risk scores
scores_df = get_risk_scores_summary()
patterns_df = pd.read_csv("../data/processed/detected_patterns.csv")

print(f"✅ Patterns loaded: {len(patterns_df)} records")
print(f"✅ Scores loaded: {len(scores_df)} records")
print(f"\nDataset Info:")
print(patterns_df.info())


# ── Cell 3: Basic Statistics ─────────────────────────────────
print("\n📊 BASIC STATISTICS")
print("="*50)
print(f"Total dark patterns detected: {len(patterns_df)}")
print(f"Unique websites: {patterns_df['website_name'].nunique()}")
print(f"Pattern categories: {patterns_df['pattern_name'].nunique()}")
print(f"\nSeverity Distribution:")
print(patterns_df['severity'].value_counts())
print(f"\nPatterns per website:")
print(patterns_df.groupby('website_name').size().sort_values(ascending=False))


# ── Cell 4: Pattern Frequency by Website ─────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Grouped bar chart
pivot = patterns_df.groupby(['website_name', 'severity']).size().unstack(fill_value=0)
pivot = pivot.reindex(columns=['HIGH', 'MEDIUM', 'LOW'], fill_value=0)
pivot.plot(kind='bar', ax=axes[0], color=['#C0392B', '#E67E22', '#27AE60'],
           edgecolor='white', width=0.7)
axes[0].set_title('Dark Patterns by Website & Severity', fontsize=14, fontweight='bold', pad=15)
axes[0].set_xlabel('Website', fontsize=11)
axes[0].set_ylabel('Number of Patterns', fontsize=11)
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=25, ha='right')
axes[0].legend(title='Severity', framealpha=0.9)
for container in axes[0].containers:
    axes[0].bar_label(container, fmt='%d', fontsize=8, padding=2)

# Total patterns per website
total_per_site = patterns_df['website_name'].value_counts()
colors_bar = ['#C0392B' if x == total_per_site.max() else '#3498DB' for x in total_per_site]
axes[1].barh(total_per_site.index, total_per_site.values, color=colors_bar, edgecolor='white')
axes[1].set_title('Total Dark Patterns Detected per Website', fontsize=14, fontweight='bold', pad=15)
axes[1].set_xlabel('Total Patterns', fontsize=11)
for i, v in enumerate(total_per_site.values):
    axes[1].text(v + 0.1, i, str(v), va='center', fontweight='bold')

plt.tight_layout(pad=3)
plt.savefig('../data/processed/eda_01_website_patterns.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 Chart saved!")


# ── Cell 5: Pattern Category Distribution ───────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Horizontal bar: Pattern types
pattern_counts = patterns_df['pattern_name'].value_counts()
colors = ['#C0392B' if 'HIGH' in patterns_df[patterns_df['pattern_name']==p]['severity'].values[0]
          else '#E67E22' if 'MEDIUM' in patterns_df[patterns_df['pattern_name']==p]['severity'].values[0]
          else '#27AE60'
          for p in pattern_counts.index]

axes[0].barh(pattern_counts.index, pattern_counts.values, color=colors, edgecolor='white', height=0.6)
axes[0].set_title('Top Dark Pattern Categories', fontsize=14, fontweight='bold', pad=15)
axes[0].set_xlabel('Occurrences', fontsize=11)
for i, v in enumerate(pattern_counts.values):
    axes[0].text(v + 0.05, i, str(v), va='center', fontsize=9, fontweight='bold')

# Pie chart: Severity share
severity_counts = patterns_df['severity'].value_counts()
explode = [0.05] * len(severity_counts)
axes[1].pie(
    severity_counts.values,
    labels=severity_counts.index,
    colors=['#C0392B', '#E67E22', '#27AE60'],
    autopct='%1.1f%%',
    explode=explode,
    startangle=90,
    textprops={'fontsize': 12, 'fontweight': 'bold'}
)
axes[1].set_title('Severity Distribution', fontsize=14, fontweight='bold', pad=15)

plt.tight_layout(pad=3)
plt.savefig('../data/processed/eda_02_pattern_types.png', dpi=150, bbox_inches='tight')
plt.show()


# ── Cell 6: Heatmap — Website vs Pattern Type ───────────────
pivot_heat = patterns_df.groupby(['website_name', 'pattern_name']).size().unstack(fill_value=0)

plt.figure(figsize=(16, 7))
sns.heatmap(
    pivot_heat,
    annot=True,
    fmt='d',
    cmap='RdYlGn_r',
    linewidths=0.5,
    linecolor='white',
    cbar_kws={'label': 'Pattern Count'}
)
plt.title('🔥 Dark Pattern Heatmap: Website vs Pattern Category',
          fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Pattern Category', fontsize=11)
plt.ylabel('Website', fontsize=11)
plt.xticks(rotation=35, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()
plt.savefig('../data/processed/eda_03_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("📊 Heatmap saved!")


# ── Cell 7: DPRS Score Comparison ───────────────────────────
if len(scores_df) > 0:
    fig = px.bar(
        scores_df.sort_values('dprs_score', ascending=False),
        x='name', y='dprs_score',
        color='compliance_status',
        color_discrete_map={
            'NON-COMPLIANT': '#C0392B',
            'AT RISK':       '#E67E22',
            'COMPLIANT':     '#27AE60'
        },
        title='🎯 Dark Pattern Risk Score (DPRS) by Website',
        labels={'name': 'Website', 'dprs_score': 'DPRS Score (0-100)'},
        text='dprs_score',
        height=450
    )
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.add_hline(y=60, line_dash="dash", line_color="red",
                  annotation_text="Non-Compliant Threshold (60)")
    fig.add_hline(y=30, line_dash="dash", line_color="orange",
                  annotation_text="At Risk Threshold (30)")
    fig.update_layout(showlegend=True, plot_bgcolor='white')
    fig.write_html('../data/processed/eda_04_dprs_scores.html')
    fig.show()


# ── Cell 8: Statistical Test — Chi-Square ───────────────────
print("\n📐 STATISTICAL ANALYSIS: Chi-Square Test")
print("="*55)
print("Hypothesis: Is there a significant difference in dark")
print("pattern frequency across websites?")
print()

contingency_table = pd.crosstab(patterns_df['website_name'], patterns_df['severity'])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print(f"Chi-Square Statistic : {chi2:.4f}")
print(f"P-Value              : {p_value:.6f}")
print(f"Degrees of Freedom   : {dof}")
print()
if p_value < 0.05:
    print("✅ RESULT: Statistically significant difference (p < 0.05)")
    print("   → Dark pattern distribution varies significantly across websites")
else:
    print("❌ RESULT: No statistically significant difference (p >= 0.05)")


# ── Cell 9: Word Cloud of Dark Pattern Evidence ─────────────
if 'evidence' in patterns_df.columns:
    all_text = ' '.join(patterns_df['evidence'].dropna().astype(str))

    wordcloud = WordCloud(
        width=1200, height=600,
        background_color='#1F2937',
        colormap='RdYlGn_r',
        max_words=100,
        collocations=False,
        min_font_size=10
    ).generate(all_text)

    plt.figure(figsize=(16, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('🔤 Word Cloud of Dark Pattern Evidence Text',
              fontsize=16, fontweight='bold', color='#1F2937', pad=20)
    plt.tight_layout()
    plt.savefig('../data/processed/eda_05_wordcloud.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("☁️  Word cloud saved!")


# ── Cell 10: EDA Summary ─────────────────────────────────────
print("\n" + "="*60)
print("📋 EDA SUMMARY")
print("="*60)
print(f"  Websites analyzed    : {patterns_df['website_name'].nunique()}")
print(f"  Total patterns found : {len(patterns_df)}")
print(f"  HIGH severity count  : {(patterns_df['severity']=='HIGH').sum()}")
print(f"  MEDIUM severity count: {(patterns_df['severity']=='MEDIUM').sum()}")
print(f"  LOW severity count   : {(patterns_df['severity']=='LOW').sum()}")
print(f"  Most common pattern  : {patterns_df['pattern_name'].mode()[0]}")
print(f"  Highest-risk website : {patterns_df['website_name'].value_counts().index[0]}")
print("="*60)
print("\n✅ EDA Complete! Proceed to Notebook 04.")
