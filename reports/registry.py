"""
XORADEX EDUCORE ERP
REPORT REGISTRY

Central registry for role-aware reports.

Reports are registered here so that new personnel,
departments and report categories can be added without
rebuilding the Reports Center.
"""


REPORT_CATEGORIES = {

    "students": {
        "label": "Students",
        "icon": "fa-solid fa-user-graduate",
    },

    "academics": {
        "label": "Academics",
        "icon": "fa-solid fa-book-open",
    },

    "finance": {
        "label": "Finance",
        "icon": "fa-solid fa-coins",
    },

    "graduation": {
        "label": "Graduation",
        "icon": "fa-solid fa-graduation-cap",
    },

    "staff": {
        "label": "Staff",
        "icon": "fa-solid fa-users",
    },

    "communication": {
        "label": "Communication",
        "icon": "fa-solid fa-comments",
    },

    "system": {
        "label": "System",
        "icon": "fa-solid fa-gears",
    },
}


REPORTS = {

    # ==========================================================
    # STUDENTS
    # ==========================================================

    "student_register": {
        "name": "Student Register",
        "category": "students",
        "description": (
            "Detailed student register for authorised users."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "HOD",
            "REGISTRAR",
        ],
    },

    "enrollment_summary": {
        "name": "Enrollment Summary",
        "category": "students",
        "description": (
            "Student enrollment summary by academic structure."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "HOD",
            "REGISTRAR",
        ],
    },

    "student_status": {
        "name": "Student Status Report",
        "category": "students",
        "description": (
            "Student numbers grouped by current status."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "HOD",
            "REGISTRAR",
        ],
    },

    # ==========================================================
    # FINANCE
    # ==========================================================

    "financial_position": {
        "name": "Financial Position",
        "category": "finance",
        "description": (
            "Expected revenue, collections, credits and "
            "outstanding balances."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "FINANCE_OFFICER",
        ],
    },

    "financial_transactions": {
        "name": "Financial Transactions",
        "category": "finance",
        "description": (
            "Detailed posted financial transactions."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "FINANCE_OFFICER",
        ],
    },

    "outstanding_fees": {
        "name": "Outstanding Fees",
        "category": "finance",
        "description": (
            "Student outstanding balances with institutional "
            "and departmental filtering."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "FINANCE_OFFICER",
            "HOD",
        ],
    },

    # ==========================================================
    # ACADEMICS
    # ==========================================================

    "examination_performance": {
        "name": "Examination Performance",
        "category": "academics",
        "description": (
            "Academic examination performance summary."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "HOD",
            "EXAMINATIONS_OFFICER",
        ],
    },

    "missing_marks": {
        "name": "Missing Marks",
        "category": "academics",
        "description": (
            "Students and academic units with incomplete results."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "HOD",
            "EXAMINATIONS_OFFICER",
        ],
    },

    # ==========================================================
    # GRADUATION
    # ==========================================================

    "graduation_eligibility": {
        "name": "Graduation Eligibility",
        "category": "graduation",
        "description": (
            "Assess students for academic and graduation eligibility."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "GRADUATION_OFFICER",
        ],
    },

    "graduation_list": {
        "name": "Graduation List",
        "category": "graduation",
        "description": (
            "Official list of approved graduation candidates."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "GRADUATION_OFFICER",
        ],
    },

    # ==========================================================
    # STAFF
    # ==========================================================

    "staff_register": {
        "name": "Staff Register",
        "category": "staff",
        "description": (
            "Institutional staff register."
        ),
        "roles": [
            "ADMIN",
            "PRINCIPAL",
            "REGISTRAR",
        ],
    },

    # ==========================================================
    # SYSTEM
    # ==========================================================

    "user_accounts": {
        "name": "User Accounts",
        "category": "system",
        "description": (
            "System user account report."
        ),
        "roles": [
            "ADMIN",
        ],
    },

    "audit_trail": {
        "name": "Audit Trail",
        "category": "system",
        "description": (
            "Recorded system activity and audit events."
        ),
        "roles": [
            "ADMIN",
        ],
    },
}


def get_report(report_key):
    """
    Return a report definition by its registry key.
    """
    return REPORTS.get(report_key)


def get_available_reports(role):
    """
    Return reports available to a given role.
    """
    role = (role or "").upper()

    return {
        key: report
        for key, report in REPORTS.items()
        if role in report.get("roles", [])
    }


def get_reports_by_category(role):
    """
    Group authorised reports by category.
    """
    available_reports = get_available_reports(role)

    grouped = {}

    for key, report in available_reports.items():

        category = report["category"]

        grouped.setdefault(
            category,
            []
        ).append(
            {
                "key": key,
                **report,
            }
        )

    return grouped