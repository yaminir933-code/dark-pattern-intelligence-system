"""
============================================================
Dark Pattern Intelligence System (DPIS)
src/report_generator.py

Automated Excel & PDF Report Generator
Generates:
  1. dark_pattern_audit_template.xlsx  - Manual audit sheet
  2. kpi_tracker.xlsx                  - Weekly KPI tracker
  3. website_scores.xlsx               - Final DPRS scores
  4. dpis_report.pdf                   - Executive summary PDF
============================================================
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, date
from openpyxl import Workbook
from openpyxl.styles import (
    Font, Fill, PatternFill, Alignment, Border, Side,
    GradientFill
)
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
import warnings
warnings.filterwarnings('ignore')


# ============================================================
# COLOR PALETTE
# ============================================================
COLORS = {
    "header_bg":    "1F3A5F",   # Dark navy blue
    "header_text":  "FFFFFF",   # White
    "high_risk":    "C0392B",   # Red
    "medium_risk":  "E67E22",   # Orange
    "low_risk":     "27AE60",   # Green
    "row_alt":      "EBF5FB",   # Light blue alternate row
    "border":       "2980B9",   # Blue border
    "title_bg":     "2C3E50",   # Dark title bg
    "accent":       "3498DB",   # Accent blue
    "compliant":    "1E8449",   # Dark green
    "at_risk":      "D68910",   # Dark orange
    "non_compliant":"922B21",   # Dark red
}


def _header_style(ws, cell_ref, text, font_size=12, bold=True):
    """Applies header styling to a cell."""
    cell = ws[cell_ref]
    cell.value = text
    cell.font = Font(name='Calibri', size=font_size, bold=bold, color=COLORS["header_text"])
    cell.fill = PatternFill("solid", fgColor=COLORS["header_bg"])
    cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    return cell


def _severity_fill(severity: str) -> PatternFill:
    """Returns background fill color based on severity."""
    colors = {
        "HIGH":   COLORS["high_risk"],
        "MEDIUM": COLORS["medium_risk"],
        "LOW":    COLORS["low_risk"]
    }
    return PatternFill("solid", fgColor=colors.get(severity, "FFFFFF"))


def _compliance_fill(status: str) -> PatternFill:
    colors = {
        "COMPLIANT":     COLORS["compliant"],
        "AT RISK":       COLORS["at_risk"],
        "NON-COMPLIANT": COLORS["non_compliant"]
    }
    return PatternFill("solid", fgColor=colors.get(status, "FFFFFF"))


# ============================================================
# EXCEL FILE 1: AUDIT TEMPLATE
# ============================================================

def create_audit_template(output_path: str):
    """
    Creates the dark pattern manual audit template Excel file.
    This is used for manually recording dark patterns with screenshots.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Audit Sheet"

    # Title Row
    ws.merge_cells("A1:J1")
    title_cell = ws["A1"]
    title_cell.value = "🕵️  Dark Pattern Intelligence System — Manual Audit Template"
    title_cell.font = Font(name='Calibri', size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill("solid", fgColor=COLORS["title_bg"])
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 40

    # Sub-header
    ws.merge_cells("A2:J2")
    ws["A2"].value = f"Last Updated: {datetime.now().strftime('%B %d, %Y')}  |  Analyst: _______________  |  Version: 1.0"
    ws["A2"].font = Font(name='Calibri', size=10, italic=True, color="555555")
    ws["A2"].alignment = Alignment(horizontal='center')

    # Column Headers
    headers = [
        ("A3", "S.No"),
        ("B3", "Website Name"),
        ("C3", "Page URL"),
        ("D3", "Page Type"),
        ("E3", "Dark Pattern Category"),
        ("F3", "Pattern Type"),
        ("G3", "Severity"),
        ("H3", "Evidence / Screenshot Description"),
        ("I3", "Date Found"),
        ("J3", "Analyst Notes"),
    ]
    for cell_ref, label in headers:
        _header_style(ws, cell_ref, label, font_size=10)

    ws.row_dimensions[3].height = 35

    # Column widths
    col_widths = [6, 18, 35, 14, 28, 18, 12, 45, 14, 35]
    for i, width in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Sample data rows (5 examples for guidance)
    sample_data = [
        (1, "Amazon India", "https://amazon.in/s?k=mobile", "Search", "Fake Scarcity",
         "Urgency", "MEDIUM", 'Displays "Only 2 left!" on multiple products simultaneously',
         date.today().isoformat(), "Verify if stock count is real"),
        (2, "Flipkart", "https://flipkart.com", "Homepage", "Fake Countdown Timer",
         "Urgency", "HIGH", 'Countdown timer showing "Deal ends in 02:30:00" — resets on refresh',
         date.today().isoformat(), "Timer resets on page reload"),
        (3, "Meesho", "https://meesho.com/checkout", "Checkout", "Pre-checked Boxes",
         "Sneaking", "HIGH", '"Add purchase protection ₹49" pre-selected without user consent',
         date.today().isoformat(), "Box unchecks only if user notices"),
        (4, "Myntra", "https://myntra.com/sale", "Deals", "Price Drip",
         "Misdirection", "HIGH", 'Delivery fee only shown at final checkout step — ₹49 added',
         date.today().isoformat(), "Not disclosed until last step"),
        (5, "Snapdeal", "https://snapdeal.com/product", "Product", "Confirm Shaming",
         "Psychological", "MEDIUM", '"No thanks, I don\'t want to save money" dismiss button',
         date.today().isoformat(), "Psychologically manipulative wording"),
    ]

    for row_num, row_data in enumerate(sample_data, start=4):
        ws.row_dimensions[row_num].height = 25
        for col_num, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.font = Font(name='Calibri', size=9)
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            if row_num % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=COLORS["row_alt"])

            # Severity color
            if col_num == 7:  # Severity column
                cell.fill = _severity_fill(str(value))
                cell.font = Font(name='Calibri', size=9, bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal='center', vertical='center')

    # Add 20 blank rows for manual entry
    for row_num in range(9, 30):
        ws.row_dimensions[row_num].height = 22
        for col_num in range(1, 11):
            cell = ws.cell(row=row_num, column=col_num, value="")
            cell.border = Border(
                bottom=Side(style='thin', color=COLORS["border"]),
                right=Side(style='thin', color=COLORS["border"])
            )
            if row_num % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F8F9FA")

    # Instructions Sheet
    ws2 = wb.create_sheet("Instructions")
    instructions = [
        ("A1", "📋 HOW TO USE THIS AUDIT TEMPLATE", 14, True),
        ("A3", "1. Visit each website listed in the 'Audit Sheet' tab", 11, False),
        ("A4", "2. Browse through homepage, search results, and product pages", 11, False),
        ("A5", "3. Note any dark patterns you find and fill in all columns", 11, False),
        ("A6", "4. Use the 'Severity' column: HIGH / MEDIUM / LOW", 11, False),
        ("A7", "5. Describe the exact text or UI element in 'Evidence' column", 11, False),
        ("A8", "6. Take a screenshot and note the filename in 'Analyst Notes'", 11, False),
        ("A10", "🔴 HIGH Severity   → Directly violates consumer protection laws", 11, False),
        ("A11", "🟡 MEDIUM Severity → Misleading but not always illegal", 11, False),
        ("A12", "🟢 LOW Severity    → Questionable but commonly accepted practice", 11, False),
    ]
    for cell_ref, text, size, bold in instructions:
        ws2[cell_ref].value = text
        ws2[cell_ref].font = Font(name='Calibri', size=size, bold=bold)
    ws2.column_dimensions['A'].width = 70

    wb.save(output_path)
    print(f"✅ Audit template saved: {output_path}")


# ============================================================
# EXCEL FILE 2: WEBSITE SCORES REPORT
# ============================================================

def create_scores_report(scores_data: list, output_path: str):
    """
    Creates the website DPRS scores Excel report with color coding.
    
    Args:
        scores_data: List of dicts with keys:
            website, dprs_score, compliance_status,
            total_patterns, high, medium, low, scan_date
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "DPRS Scores"

    # Title
    ws.merge_cells("A1:H1")
    ws["A1"].value = "🎯  Dark Pattern Risk Score (DPRS) — Website Compliance Report"
    ws["A1"].font = Font(name='Calibri', size=15, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=COLORS["title_bg"])
    ws["A1"].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 40

    ws.merge_cells("A2:H2")
    ws["A2"].value = f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}  |  DPIS v1.0"
    ws["A2"].font = Font(name='Calibri', size=10, italic=True)
    ws["A2"].alignment = Alignment(horizontal='center')

    # Column Headers
    col_headers = [
        "Website", "DPRS Score (0–100)", "Compliance Status",
        "Total Patterns", "🔴 HIGH", "🟡 MEDIUM", "🟢 LOW", "Scan Date"
    ]
    for col, header in enumerate(col_headers, start=1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = Font(name='Calibri', size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=COLORS["header_bg"])
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[3].height = 35

    # Data rows
    for row_num, entry in enumerate(scores_data, start=4):
        data = [
            entry.get("website", ""),
            entry.get("dprs_score", 0),
            entry.get("compliance_status", ""),
            entry.get("total_patterns", 0),
            entry.get("high", 0),
            entry.get("medium", 0),
            entry.get("low", 0),
            entry.get("scan_date", date.today().isoformat()),
        ]
        ws.row_dimensions[row_num].height = 28
        for col_num, value in enumerate(data, start=1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.font = Font(name='Calibri', size=10)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if row_num % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="EBF5FB")

        # Color DPRS score cell
        score_cell = ws.cell(row=row_num, column=2)
        score = entry.get("dprs_score", 0)
        if score <= 30:
            score_cell.fill = PatternFill("solid", fgColor="ABEBC6")  # Green
        elif score <= 60:
            score_cell.fill = PatternFill("solid", fgColor="FAD7A0")  # Orange
        else:
            score_cell.fill = PatternFill("solid", fgColor="F1948A")  # Red
        score_cell.font = Font(name='Calibri', size=11, bold=True)

        # Color compliance cell
        status_cell = ws.cell(row=row_num, column=3)
        status_cell.fill = _compliance_fill(str(entry.get("compliance_status", "")))
        status_cell.font = Font(name='Calibri', size=10, bold=True, color="FFFFFF")

    # Column widths
    col_widths = [20, 20, 22, 18, 10, 12, 10, 16]
    for i, width in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Add Bar Chart
    if scores_data:
        chart = BarChart()
        chart.type = "col"
        chart.title = "DPRS Score by Website"
        chart.y_axis.title = "DPRS Score (0-100)"
        chart.x_axis.title = "Website"
        chart.style = 10
        chart.width = 20
        chart.height = 12

        data_ref = Reference(ws, min_col=2, max_col=2,
                              min_row=3, max_row=3 + len(scores_data))
        cats = Reference(ws, min_col=1, min_row=4, max_row=3 + len(scores_data))
        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, "A" + str(5 + len(scores_data)))

    wb.save(output_path)
    print(f"✅ Scores report saved: {output_path}")


# ============================================================
# EXCEL FILE 3: KPI TRACKER
# ============================================================

def create_kpi_tracker(output_path: str):
    """
    Creates a weekly KPI tracker Excel workbook.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "KPI Tracker"

    ws.merge_cells("A1:G1")
    ws["A1"].value = "📊  DPIS — Weekly KPI Tracker"
    ws["A1"].font = Font(name='Calibri', size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=COLORS["title_bg"])
    ws["A1"].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 36

    # KPI Headers
    kpi_headers = ["Week", "Total Pages Scanned", "Total Patterns Found",
                   "HIGH Severity", "MEDIUM Severity", "LOW Severity", "Avg DPRS Score"]
    for col, header in enumerate(kpi_headers, start=1):
        cell = ws.cell(row=2, column=col, value=header)
        cell.font = Font(name='Calibri', size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=COLORS["header_bg"])
        cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 30

    # Sample weekly data
    sample_weeks = [
        ("Week 1", 20, 45, 18, 15, 12, 72.5),
        ("Week 2", 25, 52, 20, 18, 14, 68.3),
        ("Week 3", 30, 48, 15, 20, 13, 61.7),
        ("Week 4", 35, 40, 12, 17, 11, 54.2),
    ]
    for row_num, row_data in enumerate(sample_weeks, start=3):
        ws.row_dimensions[row_num].height = 24
        for col_num, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.font = Font(name='Calibri', size=10)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            if row_num % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="EBF5FB")

    for i, width in enumerate([12, 22, 22, 16, 18, 14, 18], start=1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Line chart for DPRS trend
    chart = BarChart()
    chart.type = "col"
    chart.title = "Weekly DPRS Score Trend"
    chart.y_axis.title = "Avg DPRS Score"
    chart.style = 10
    chart.width = 18
    chart.height = 10

    data_ref = Reference(ws, min_col=7, max_col=7, min_row=2, max_row=6)
    cats = Reference(ws, min_col=1, min_row=3, max_row=6)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "A8")

    wb.save(output_path)
    print(f"✅ KPI tracker saved: {output_path}")


# ============================================================
# MAIN: Generate all Excel reports
# ============================================================
if __name__ == "__main__":
    output_dir = "../data/excel"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Audit Template
    create_audit_template(f"{output_dir}/dark_pattern_audit_template.xlsx")

    # 2. Sample Scores Report
    sample_scores = [
        {"website": "Amazon India", "dprs_score": 78.5, "compliance_status": "NON-COMPLIANT",
         "total_patterns": 9, "high": 5, "medium": 3, "low": 1, "scan_date": "2025-01-15"},
        {"website": "Flipkart",     "dprs_score": 65.2, "compliance_status": "NON-COMPLIANT",
         "total_patterns": 7, "high": 4, "medium": 2, "low": 1, "scan_date": "2025-01-15"},
        {"website": "Meesho",       "dprs_score": 45.0, "compliance_status": "AT RISK",
         "total_patterns": 5, "high": 2, "medium": 2, "low": 1, "scan_date": "2025-01-15"},
        {"website": "Myntra",       "dprs_score": 38.5, "compliance_status": "AT RISK",
         "total_patterns": 4, "high": 1, "medium": 2, "low": 1, "scan_date": "2025-01-15"},
        {"website": "Snapdeal",     "dprs_score": 22.0, "compliance_status": "COMPLIANT",
         "total_patterns": 2, "high": 0, "medium": 1, "low": 1, "scan_date": "2025-01-15"},
    ]
    create_scores_report(sample_scores, f"{output_dir}/website_scores.xlsx")

    # 3. KPI Tracker
    create_kpi_tracker(f"{output_dir}/kpi_tracker.xlsx")

    print("\n🎉 All Excel reports generated successfully!")
