from io import BytesIO
from decimal import Decimal

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


# ============================================================
# STUDENT MASTER REGISTER PDF
# ============================================================

def create_student_register_pdf(rows):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Student Master Register",
        author="XORADEX EDUCORE ERP",
    )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        spaceAfter=12,
    )

    cell_style = ParagraphStyle(
        "ReportCell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
    )

    header_style = ParagraphStyle(
        "ReportHeader",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.white,
    )

    # --------------------------------------------------------
    # DOCUMENT CONTENT
    # --------------------------------------------------------

    story = []

    story.append(
        Paragraph(
            "XORADEX EDUCORE ERP",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Student Master Register",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Total Students: {len(rows)}",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    # --------------------------------------------------------
    # TABLE HEADERS
    # --------------------------------------------------------

    headers = [
        "Admission No.",
        "Student Name",
        "Gender",
        "Department",
        "Course",
        "Programme",
        "Admission Date",
        "Status",
    ]

    data = [
        [
            Paragraph(
                header,
                header_style,
            )
            for header in headers
        ]
    ]

    # --------------------------------------------------------
    # TABLE DATA
    # --------------------------------------------------------

    for row in rows:

        admission_date = row.get("admission_date")

        if admission_date:

            admission_date = admission_date.strftime(
                "%d %b %Y"
            )

        else:

            admission_date = "—"

        data.append(
            [
                Paragraph(
                    str(
                        row.get("admission_no")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("name")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("gender")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("department")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("course")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("programme")
                        or "—"
                    ),
                    cell_style,
                ),

                Paragraph(
                    admission_date,
                    cell_style,
                ),

                Paragraph(
                    str(
                        row.get("status")
                        or "—"
                    ),
                    cell_style,
                ),
            ]
        )

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            25 * mm,
            38 * mm,
            18 * mm,
            32 * mm,
            32 * mm,
            45 * mm,
            25 * mm,
            22 * mm,
        ],
    )

    # --------------------------------------------------------
    # TABLE STYLING
    # --------------------------------------------------------

    table.setStyle(
        TableStyle(
            [

                # Header
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                # Vertical alignment
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                # Grid
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),

                # Padding
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                # Alternating rows
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
            ]
        )
    )

    story.append(table)

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# FINANCIAL TRANSACTIONS PDF
# ============================================================

def _money(value):

    return float(
        value or Decimal("0.00")
    )


def _percentage(value):

    return float(
        value or Decimal("0.00")
    )


def create_financial_transactions_pdf(report):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Financial Transactions & Performance Report",
        author="XORADEX EDUCORE ERP",
    )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "FinancialReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        leading=20,
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
        "FinancialReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        leading=12,
        spaceAfter=12,
    )

    header_style = ParagraphStyle(
        "FinancialReportHeader",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.white,
    )

    cell_style = ParagraphStyle(
        "FinancialReportCell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
    )

    # --------------------------------------------------------
    # REPORT DATA
    # --------------------------------------------------------

    summary = report.get("summary", {})

    current = report.get(
        "current_semester",
        {},
    )

    previous = report.get(
        "previous_semester",
        {},
    )

    historical = report.get(
        "historical",
        [],
    )

    departments = report.get(
        "departments",
        [],
    )

    transactions = report.get(
        "transactions",
        [],
    )

    # --------------------------------------------------------
    # DOCUMENT CONTENT
    # --------------------------------------------------------

    story = []

    story.append(
        Paragraph(
            "XORADEX EDUCORE ERP",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Financial Transactions & Performance Report",
            subtitle_style,
        )
    )

    current_semester_name = (
        report.get("current_semester_name")
        or current.get("semester_name")
        or "Current Semester"
    )

    previous_semester_name = (
        report.get("previous_semester_name")
        or previous.get("semester_name")
        or "Previous Semester"
    )

    story.append(
        Paragraph(
            f"Current Semester: {current_semester_name}",
            styles["Normal"],
        )
    )

    story.append(
        Paragraph(
            f"Previous Semester: {previous_semester_name}",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    # --------------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Executive Summary",
            styles["Heading2"],
        )
    )

    summary_data = [
        [
            Paragraph(
                "Metric",
                header_style,
            ),
            Paragraph(
                "Amount",
                header_style,
            ),
        ],
        [
            Paragraph(
                "Gross Invoiced",
                cell_style,
            ),
            Paragraph(
                f"{_money(summary.get('gross_invoiced')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph(
                "Cash Collections",
                cell_style,
            ),
            Paragraph(
                f"{_money(summary.get('cash_collections')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph(
                "Credits Applied",
                cell_style,
            ),
            Paragraph(
                f"{_money(summary.get('credits_applied')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph(
                "Outstanding Balance",
                cell_style,
            ),
            Paragraph(
                f"{_money(summary.get('outstanding')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph(
                "Settlement Rate",
                cell_style,
            ),
            Paragraph(
                f"{_percentage(summary.get('settlement_rate')):.1f}%",
                cell_style,
            ),
        ],
        [
            Paragraph(
                "Cash Collection Rate",
                cell_style,
            ),
            Paragraph(
                f"{_percentage(summary.get('cash_collection_rate')):.1f}%",
                cell_style,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            65 * mm,
            45 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # CURRENT VS PREVIOUS SEMESTER
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Current vs Previous Semester",
            styles["Heading2"],
        )
    )

    comparison_data = [
        [
            Paragraph("Metric", header_style),
            Paragraph("Current", header_style),
            Paragraph("Previous", header_style),
        ],
        [
            Paragraph("Gross Invoiced", cell_style),
            Paragraph(
                f"{_money(current.get('gross_invoiced')):,.2f}",
                cell_style,
            ),
            Paragraph(
                f"{_money(previous.get('gross_invoiced')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph("Cash Collections", cell_style),
            Paragraph(
                f"{_money(current.get('cash_collections')):,.2f}",
                cell_style,
            ),
            Paragraph(
                f"{_money(previous.get('cash_collections')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph("Credits Applied", cell_style),
            Paragraph(
                f"{_money(current.get('credits_applied')):,.2f}",
                cell_style,
            ),
            Paragraph(
                f"{_money(previous.get('credits_applied')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph("Outstanding", cell_style),
            Paragraph(
                f"{_money(current.get('outstanding')):,.2f}",
                cell_style,
            ),
            Paragraph(
                f"{_money(previous.get('outstanding')):,.2f}",
                cell_style,
            ),
        ],
        [
            Paragraph("Settlement Rate", cell_style),
            Paragraph(
                f"{_percentage(current.get('settlement_rate')):.1f}%",
                cell_style,
            ),
            Paragraph(
                f"{_percentage(previous.get('settlement_rate')):.1f}%",
                cell_style,
            ),
        ],
        [
            Paragraph("Cash Collection Rate", cell_style),
            Paragraph(
                f"{_percentage(current.get('cash_collection_rate')):.1f}%",
                cell_style,
            ),
            Paragraph(
                f"{_percentage(previous.get('cash_collection_rate')):.1f}%",
                cell_style,
            ),
        ],
    ]

    comparison_table = Table(
        comparison_data,
        colWidths=[
            65 * mm,
            45 * mm,
            45 * mm,
        ],
    )

    comparison_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
            ]
        )
    )

    story.append(comparison_table)

    story.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # HISTORICAL PERFORMANCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Historical Performance",
            styles["Heading2"],
        )
    )

    historical_data = [
        [
            Paragraph("Semester", header_style),
            Paragraph("Gross Invoiced", header_style),
            Paragraph("Cash Collections", header_style),
            Paragraph("Credits Applied", header_style),
            Paragraph("Outstanding", header_style),
            Paragraph("Settlement Rate", header_style),
        ]
    ]

    for row in historical:

        historical_data.append(
            [
                Paragraph(
                    str(
                        row.get("semester_name")
                        or row.get("semester")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('gross_invoiced')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('cash_collections')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('credits_applied')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('outstanding')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_percentage(row.get('settlement_rate')):.1f}%",
                    cell_style,
                ),
            ]
        )

    historical_table = Table(
        historical_data,
        repeatRows=1,
        colWidths=[
            45 * mm,
            35 * mm,
            35 * mm,
            35 * mm,
            35 * mm,
            30 * mm,
        ],
    )

    historical_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
            ]
        )
    )

    story.append(historical_table)

    story.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # DEPARTMENT PERFORMANCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Department Performance",
            styles["Heading2"],
        )
    )

    department_data = [
        [
            Paragraph("Department", header_style),
            Paragraph("Gross Invoiced", header_style),
            Paragraph("Cash Collections", header_style),
            Paragraph("Credits Applied", header_style),
            Paragraph("Outstanding", header_style),
            Paragraph("Settlement Rate", header_style),
        ]
    ]

    for row in departments:

        department_data.append(
            [
                Paragraph(
                    str(
                        row.get("department_name")
                        or row.get("department")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('gross_invoiced')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('cash_collections')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('credits_applied')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('outstanding')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    f"{_percentage(row.get('settlement_rate')):.1f}%",
                    cell_style,
                ),
            ]
        )

    department_table = Table(
        department_data,
        repeatRows=1,
        colWidths=[
            50 * mm,
            35 * mm,
            35 * mm,
            35 * mm,
            35 * mm,
            30 * mm,
        ],
    )

    department_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
            ]
        )
    )

    story.append(department_table)

    story.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # POSTED TRANSACTIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Detailed Posted Transactions",
            styles["Heading2"],
        )
    )

    transaction_data = [
        [
            Paragraph("Payment No.", header_style),
            Paragraph("Student", header_style),
            Paragraph("Admission No.", header_style),
            Paragraph("Department", header_style),
            Paragraph("Programme", header_style),
            Paragraph("Amount", header_style),
            Paragraph("Payment Method", header_style),
            Paragraph("Payment Date", header_style),
            Paragraph("Reference", header_style),
        ]
    ]

    for row in transactions:

        payment_date = row.get(
            "payment_date"
        )

        if payment_date:

            try:
                payment_date = payment_date.strftime(
                    "%d %b %Y"
                )
            except AttributeError:
                payment_date = str(
                    payment_date
                )

        else:

            payment_date = "—"

        transaction_data.append(
            [
                Paragraph(
                    str(
                        row.get("payment_number")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("student_name")
                        or row.get("student")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("admission_number")
                        or row.get("admission_no")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("department_name")
                        or row.get("department")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("programme_name")
                        or row.get("programme")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    f"{_money(row.get('amount')):,.2f}",
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("payment_method")
                        or "—"
                    ),
                    cell_style,
                ),
                Paragraph(
                    payment_date,
                    cell_style,
                ),
                Paragraph(
                    str(
                        row.get("reference_number")
                        or row.get("reference")
                        or "—"
                    ),
                    cell_style,
                ),
            ]
        )

    transaction_table = Table(
        transaction_data,
        repeatRows=1,
        colWidths=[
            25 * mm,
            35 * mm,
            27 * mm,
            32 * mm,
            40 * mm,
            25 * mm,
            28 * mm,
            25 * mm,
            30 * mm,
        ],
    )

    transaction_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#012169"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D9DEE7"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#F5F7FA"),
                    ],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    story.append(transaction_table)

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# PDF HTTP RESPONSE
# ============================================================

def pdf_response(buffer, filename):

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )

    # Force immediate download rather than browser preview.
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{filename}"'

    return response