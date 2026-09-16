"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/pdf_report_generator.py

Generates professional Executive PDF Audit Reports for Clients/Executives.
============================================================
"""

import sys
import os

# ── Setup Path Imports ───────────────────────────────────────
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(file_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fpdf import FPDF
from datetime import date
import pandas as pd
from src.db_connector import get_risk_scores_summary


class ExecutivePDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(31, 58, 95)  # Navy Primary
        self.cell(0, 10, 'Dark Pattern Intelligence System (DPIS)', border=0, ln=1, align='L')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, 'Executive Compliance Audit & Risk Assessment Report', border=0, ln=1, align='L')
        self.line(10, 28, 200, 28)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Client Audit | Generated on {date.today().isoformat()}', border=0, align='C')


def generate_pdf_report(output_path: str = "data/excel/DPIS_Executive_Audit_Report.pdf") -> str:
    """
    Generates a PDF executive summary report based on database records.
    """
    pdf = ExecutivePDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Title Banner
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, '1. Executive Summary', ln=1)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    summary_text = (
        "This audit report summarizes the automated compliance evaluation conducted across major e-commerce platforms. "
        "Each platform was evaluated against 12 recognized dark pattern categories under Indian Consumer Protection regulations "
        "(CCPA 2023) and international UX compliance standards. The Dark Pattern Risk Score (DPRS) measures platform risk on a 0-100 scale."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(5)

    # 2. Key Risk Summary Table
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, '2. Platform DPRS Risk Summary', ln=1)

    scores_df = get_risk_scores_summary()
    
    # Table Header
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(31, 58, 95)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 8, 'Website', border=1, fill=True)
    pdf.cell(30, 8, 'DPRS Score', border=1, fill=True)
    pdf.cell(40, 8, 'Status', border=1, fill=True)
    pdf.cell(35, 8, 'Patterns Found', border=1, fill=True)
    pdf.cell(45, 8, 'High Severity', border=1, fill=True, ln=1)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(40, 40, 40)
    
    for idx, row in scores_df.iterrows():
        status = str(row['compliance_status'])
        if status == 'NON-COMPLIANT':
            pdf.set_fill_color(253, 232, 232)
        elif status == 'AT RISK':
            pdf.set_fill_color(254, 243, 199)
        else:
            pdf.set_fill_color(209, 250, 229)

        pdf.cell(40, 8, str(row['name']), border=1)
        pdf.cell(30, 8, f"{row['dprs_score']:.1f}", border=1)
        pdf.cell(40, 8, status, border=1, fill=True)
        pdf.cell(35, 8, str(row['total_patterns']), border=1)
        pdf.cell(45, 8, str(row['high_severity']), border=1, ln=1)

    pdf.ln(8)

    # 3. Compliance Guidelines & Remediation Roadmap
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, '3. Regulatory Remediation Roadmap', ln=1)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    remediation_text = (
        "- Urgency Patterns (Fake Countdown Timers, Scarcity): Remove hardcoded timer resets to comply with CCPA Section 4 guidelines.\n"
        "- Sneaking Patterns (Pre-checked Boxes, Hidden Subscriptions): Ensure explicit opt-in checkboxes for auto-renewals.\n"
        "- Misdirection Patterns (Price Drip): Disclose all mandatory convenience/delivery fees upfront on product listing pages."
    )
    pdf.multi_cell(0, 6, remediation_text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"✅ Executive PDF Audit Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_pdf_report()
