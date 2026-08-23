"""
============================================================
Dark Pattern Intelligence System (DPIS)
app/app.py

Streamlit Web Application
Deployed on Render: https://dpis-app.onrender.com
============================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime, date
import time

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="DPIS — Dark Pattern Intelligence System",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1F3A5F 0%, #2C3E50 50%, #1a252f 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #AED6F1;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1F2937, #111827);
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 12px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-3px); }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #3B82F6;
        line-height: 1;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-top: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .risk-high   { color: #EF4444 !important; }
    .risk-medium { color: #F59E0B !important; }
    .risk-low    { color: #10B981 !important; }
    
    .badge-high   { background: #7F1D1D; color: #FCA5A5; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
    .badge-medium { background: #78350F; color: #FCD34D; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
    .badge-low    { background: #064E3B; color: #6EE7B7; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
    
    .dprs-compliant     { background: #064E3B; color: #34D399; padding: 5px 16px; border-radius: 20px; font-weight: 700; }
    .dprs-at-risk       { background: #78350F; color: #FCD34D; padding: 5px 16px; border-radius: 20px; font-weight: 700; }
    .dprs-non-compliant { background: #7F1D1D; color: #FCA5A5; padding: 5px 16px; border-radius: 20px; font-weight: 700; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(31,41,55,0.5);
        border-radius: 10px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #9CA3AF;
        font-weight: 500;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: #1D4ED8 !important;
        color: white !important;
    }
    
    .sidebar-section {
        background: rgba(31,41,55,0.6);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(59,130,246,0.2);
    }
</style>
""", unsafe_allow_html=True)


# ── Sample Data (replace with DB queries in production) ─────
@st.cache_data
def load_sample_data():
    """Load sample data — replace with db_connector queries in production."""
    websites = ["Amazon India", "Flipkart", "Meesho", "Myntra", "Snapdeal"]
    
    scores_data = pd.DataFrame({
        "website":            websites,
        "dprs_score":         [78.5, 65.2, 45.0, 38.5, 22.0],
        "compliance_status":  ["NON-COMPLIANT", "NON-COMPLIANT", "AT RISK", "AT RISK", "COMPLIANT"],
        "total_patterns":     [9, 7, 5, 4, 2],
        "high_severity":      [5, 4, 2, 1, 0],
        "medium_severity":    [3, 2, 2, 2, 1],
        "low_severity":       [1, 1, 1, 1, 1],
        "pages_scanned":      [18, 15, 12, 10, 8],
        "scan_date":          [date.today().isoformat()] * 5
    })

    patterns_data = pd.DataFrame({
        "website":      ["Amazon India"]*4 + ["Flipkart"]*3 + ["Meesho"]*2 + ["Myntra"]*2 + ["Snapdeal"],
        "pattern_name": [
            "Fake Countdown Timer", "Fake Scarcity", "Pre-checked Boxes", "Price Drip",
            "Fake Countdown Timer", "Hidden Subscription", "Confirm Shaming",
            "Fake Scarcity", "Price Drip",
            "Roach Motel", "Fake Countdown Timer",
            "Disguised Ads"
        ],
        "pattern_type": [
            "Urgency", "Urgency", "Sneaking", "Misdirection",
            "Urgency", "Trick", "Psychological",
            "Urgency", "Misdirection",
            "Obstruction", "Urgency",
            "Misdirection"
        ],
        "severity": [
            "HIGH", "MEDIUM", "HIGH", "HIGH",
            "HIGH", "HIGH", "MEDIUM",
            "MEDIUM", "HIGH",
            "HIGH", "HIGH",
            "MEDIUM"
        ],
        "confidence": [0.95, 0.85, 0.92, 0.88,
                       0.90, 0.95, 0.82,
                       0.78, 0.91,
                       0.87, 0.93,
                       0.80]
    })

    trend_data = pd.DataFrame({
        "week":       ["Week 1", "Week 2", "Week 3", "Week 4"],
        "Amazon India": [78.5, 80.1, 77.3, 78.5],
        "Flipkart":     [65.2, 67.0, 63.5, 65.2],
        "Meesho":       [45.0, 47.2, 44.1, 45.0],
        "Myntra":       [38.5, 40.0, 37.2, 38.5],
        "Snapdeal":     [22.0, 24.5, 21.3, 22.0],
    })
    
    return scores_data, patterns_data, trend_data


scores_df, patterns_df, trend_df = load_sample_data()


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem;'>
        <span style='font-size:2.5rem'>🕵️</span>
        <h2 style='color:#3B82F6; margin:0.3rem 0;'>DPIS</h2>
        <p style='color:#9CA3AF; font-size:0.8rem; margin:0'>Dark Pattern Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("**🔍 Filter Options**")
    selected_websites = st.multiselect(
        "Select Websites",
        options=scores_df["website"].tolist(),
        default=scores_df["website"].tolist()
    )
    selected_severity = st.multiselect(
        "Filter by Severity",
        options=["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.markdown("**📅 Scan Info**")
    st.markdown(f"Last scan: `{date.today().isoformat()}`")
    st.markdown(f"Total websites: `{len(scores_df)}`")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("👩‍💻 Built by Yamini Reddy")
    st.caption("🔗 [GitHub](#) · [LinkedIn](#)")


# Apply filters
filtered_scores   = scores_df[scores_df["website"].isin(selected_websites)]
filtered_patterns = patterns_df[
    (patterns_df["website"].isin(selected_websites)) &
    (patterns_df["severity"].isin(selected_severity))
]


# ══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class='main-header'>
    <h1>🕵️ Dark Pattern Intelligence System</h1>
    <p>Automated detection & scoring of manipulative UX patterns across major Indian e-commerce platforms</p>
</div>
""", unsafe_allow_html=True)


# ── KPI METRICS ROW ──────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

metrics = [
    (col1, len(filtered_scores), "Websites Scanned", "🌐"),
    (col2, filtered_patterns['total_patterns'].sum() if 'total_patterns' in filtered_scores.columns else len(filtered_patterns), "Patterns Found", "🚨"),
    (col3, (filtered_patterns['severity'] == 'HIGH').sum(), "HIGH Severity", "🔴"),
    (col4, f"{filtered_scores['dprs_score'].mean():.1f}", "Avg DPRS Score", "📊"),
    (col5, (filtered_scores['compliance_status'] == 'NON-COMPLIANT').sum(), "Non-Compliant", "⚠️"),
]

for col, value, label, icon in metrics:
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div style='font-size:1.6rem'>{icon}</div>
            <div class='metric-value'>{value}</div>
            <div class='metric-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── TABS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview Dashboard",
    "🔍 Pattern Deep Dive",
    "📈 Trend Analysis",
    "🔎 Live Scanner"
])


# ────────────────────────────────────────────────────────────
# TAB 1: Overview Dashboard
# ────────────────────────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        # DPRS Score Bar Chart
        fig_dprs = px.bar(
            filtered_scores.sort_values('dprs_score', ascending=True),
            x='dprs_score', y='website',
            orientation='h',
            color='compliance_status',
            color_discrete_map={
                'NON-COMPLIANT': '#EF4444',
                'AT RISK':       '#F59E0B',
                'COMPLIANT':     '#10B981'
            },
            text='dprs_score',
            title='🎯 Dark Pattern Risk Score (DPRS) per Website',
            labels={'dprs_score': 'DPRS Score (0-100)', 'website': ''}
        )
        fig_dprs.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_dprs.add_vline(x=60, line_dash="dash", line_color="#EF4444", line_width=2,
                            annotation_text="⚠ Non-Compliant (60)")
        fig_dprs.add_vline(x=30, line_dash="dash", line_color="#F59E0B", line_width=2,
                            annotation_text="⚡ At Risk (30)")
        fig_dprs.update_layout(
            plot_bgcolor='rgba(17,24,39,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E5E7EB',
            height=380,
            showlegend=True,
            xaxis=dict(range=[0, 105], gridcolor='rgba(75,85,99,0.3)'),
            yaxis=dict(gridcolor='rgba(75,85,99,0.3)')
        )
        st.plotly_chart(fig_dprs, use_container_width=True)

    with col_r:
        # Severity Pie Chart
        sev_counts = filtered_patterns['severity'].value_counts()
        fig_pie = px.pie(
            values=sev_counts.values,
            names=sev_counts.index,
            color=sev_counts.index,
            color_discrete_map={'HIGH': '#EF4444', 'MEDIUM': '#F59E0B', 'LOW': '#10B981'},
            title='🔴 Severity Distribution',
            hole=0.5
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E5E7EB',
            height=380
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Website Compliance Table
    st.markdown("### 📋 Website Compliance Summary")
    for _, row in filtered_scores.iterrows():
        score = row['dprs_score']
        status = row['compliance_status']
        badge_class = "dprs-compliant" if status == "COMPLIANT" else \
                      "dprs-at-risk" if status == "AT RISK" else "dprs-non-compliant"
        
        score_color = "#10B981" if score <= 30 else "#F59E0B" if score <= 60 else "#EF4444"
        bar_width = int(score)

        st.markdown(f"""
        <div style='background:rgba(31,41,55,0.7); border-radius:12px; padding:1.2rem; 
                    margin-bottom:0.8rem; border:1px solid rgba(75,85,99,0.4);'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;'>
                <strong style='color:#F9FAFB; font-size:1rem;'>{row['website']}</strong>
                <span class='{badge_class}'>{status}</span>
            </div>
            <div style='background:rgba(75,85,99,0.3); border-radius:8px; height:10px; overflow:hidden;'>
                <div style='background:{score_color}; width:{bar_width}%; height:100%; border-radius:8px; 
                            transition: width 0.5s ease;'></div>
            </div>
            <div style='display:flex; justify-content:space-between; margin-top:0.4rem;'>
                <span style='color:#9CA3AF; font-size:0.82rem;'>Patterns: {row['total_patterns']} | 
                    🔴 {row['high_severity']} · 🟡 {row['medium_severity']} · 🟢 {row['low_severity']}</span>
                <span style='color:{score_color}; font-weight:700;'>DPRS: {score:.1f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# TAB 2: Pattern Deep Dive
# ────────────────────────────────────────────────────────────
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        # Heatmap
        pivot = filtered_patterns.groupby(['website', 'pattern_name']).size().unstack(fill_value=0)
        fig_heat = px.imshow(
            pivot,
            color_continuous_scale='RdYlGn_r',
            title='🔥 Dark Pattern Heatmap: Website vs Pattern',
            aspect='auto',
            labels=dict(color="Count")
        )
        fig_heat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E5E7EB',
            height=420
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_r:
        # Pattern frequency
        pat_counts = filtered_patterns.groupby(['pattern_name', 'severity']).size().reset_index(name='count')
        fig_pat = px.bar(
            pat_counts,
            x='count', y='pattern_name',
            color='severity',
            color_discrete_map={'HIGH': '#EF4444', 'MEDIUM': '#F59E0B', 'LOW': '#10B981'},
            orientation='h',
            title='📊 Pattern Frequency by Severity',
            labels={'count': 'Occurrences', 'pattern_name': ''}
        )
        fig_pat.update_layout(
            plot_bgcolor='rgba(17,24,39,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E5E7EB',
            height=420
        )
        st.plotly_chart(fig_pat, use_container_width=True)

    # Pattern Details Table
    st.markdown("### 🔍 Detailed Pattern Records")
    display_df = filtered_patterns[['website', 'pattern_name', 'pattern_type', 'severity', 'confidence']].copy()
    display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
    display_df.columns = ['Website', 'Pattern', 'Type', 'Severity', 'Confidence']
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────
# TAB 3: Trend Analysis
# ────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📈 DPRS Score Trend Over 4 Weeks")
    trend_melted = trend_df.melt(id_vars='week', var_name='website', value_name='dprs_score')
    trend_melted = trend_melted[trend_melted['website'].isin(selected_websites)]

    fig_trend = px.line(
        trend_melted,
        x='week', y='dprs_score', color='website',
        markers=True,
        title='📈 DPRS Score Weekly Trend',
        labels={'dprs_score': 'DPRS Score', 'week': 'Week', 'website': 'Website'}
    )
    fig_trend.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Non-Compliant Threshold")
    fig_trend.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="At Risk Threshold")
    fig_trend.update_layout(
        plot_bgcolor='rgba(17,24,39,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#E5E7EB',
        height=420,
        hovermode='x unified'
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Download report
    csv = filtered_scores.to_csv(index=False)
    st.download_button(
        label="📥 Download DPRS Report (CSV)",
        data=csv,
        file_name=f"dprs_report_{date.today().isoformat()}.csv",
        mime="text/csv"
    )


# ────────────────────────────────────────────────────────────
# TAB 4: Live Scanner
# ────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🔎 Live Website Dark Pattern Scanner")
    st.info("Enter any e-commerce website URL to scan it for dark patterns in real time.")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        scan_url = st.text_input(
            "Enter website URL",
            placeholder="https://www.example.com",
            label_visibility="collapsed"
        )
    with col_btn:
        scan_clicked = st.button("🔍 Scan Now", type="primary", use_container_width=True)

    if scan_clicked and scan_url:
        with st.spinner(f"🔍 Scanning {scan_url} for dark patterns..."):
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.025)
                progress.progress(i + 1)

        # Simulate scan results
        st.success(f"✅ Scan complete for: `{scan_url}`")
        
        demo_results = [
            {"pattern": "Fake Countdown Timer", "severity": "HIGH", "confidence": "94%",
             "evidence": "Timer showing '02:30:00' detected — resets on page refresh"},
            {"pattern": "Fake Scarcity",        "severity": "MEDIUM", "confidence": "87%",
             "evidence": "Text: 'Only 3 left in stock!' found on 8 products simultaneously"},
        ]

        col_score, col_status = st.columns(2)
        with col_score:
            st.markdown("""
            <div class='metric-card'>
                <div style='font-size:1.5rem'>📊</div>
                <div class='metric-value'>72.5</div>
                <div class='metric-label'>DPRS Score</div>
            </div>""", unsafe_allow_html=True)
        with col_status:
            st.markdown("""
            <div class='metric-card'>
                <div style='font-size:1.5rem'>🚨</div>
                <div class='metric-value' style='color:#EF4444'>NON-COMPLIANT</div>
                <div class='metric-label'>Compliance Status</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔴 Detected Dark Patterns:**")
        for r in demo_results:
            sev_color = "#EF4444" if r['severity'] == 'HIGH' else "#F59E0B"
            st.markdown(f"""
            <div style='background:rgba(31,41,55,0.8); border-left:4px solid {sev_color};
                        padding:1rem; border-radius:0 10px 10px 0; margin-bottom:0.8rem;'>
                <strong style='color:#F9FAFB;'>{r['pattern']}</strong> 
                <span style='color:{sev_color}; margin-left:10px; font-size:0.82rem; font-weight:600;'>
                    ● {r['severity']}
                </span>
                <span style='color:#6B7280; float:right; font-size:0.82rem;'>Confidence: {r['confidence']}</span>
                <p style='color:#9CA3AF; margin:0.5rem 0 0; font-size:0.88rem;'>{r['evidence']}</p>
            </div>
            """, unsafe_allow_html=True)
    elif scan_clicked:
        st.warning("⚠️ Please enter a valid URL to scan.")


# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#6B7280; font-size:0.85rem; padding:1rem;'>
    🕵️ <strong style='color:#3B82F6;'>Dark Pattern Intelligence System</strong> · 
    Built by <strong>Yamini Reddy</strong> · 
    Powered by Python · PostgreSQL · Streamlit · 
    <a href='#' style='color:#3B82F6;'>GitHub</a>
</div>
""", unsafe_allow_html=True)
