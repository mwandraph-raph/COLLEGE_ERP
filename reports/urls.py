from django.urls import path

from . import views


urlpatterns = [

    # ==========================================================
    # REPORTS CENTER
    # ==========================================================

    path(
        "",
        views.report_center,
        name="report_center",
    ),

    # ==========================================================
    # STAFF REGISTER
    # ==========================================================

    path(
        "staff/register/",
        views.staff_register,
        name="staff_register",
    ),

    path(
        "staff/register/excel/",
        views.staff_register_excel,
        name="staff_register_excel",
    ),

    # ==========================================================
    # STUDENT MASTER REGISTER
    # ==========================================================

    path(
        "students/register/",
        views.student_register_report,
        name="student_register_report",
    ),

    path(
        "students/register/excel/",
        views.student_register_excel,
        name="student_register_excel",
    ),

    path(
        "students/register/pdf/",
        views.student_register_pdf,
        name="student_register_pdf",
    ),

    path(
        "students/register/search/",
        views.student_register_ajax_search,
        name="student_register_ajax_search",
    ),

    # ==========================================================
    # ENROLLMENT SUMMARY
    # ==========================================================

    path(
        "students/enrollment-summary/",
        views.enrollment_summary,
        name="enrollment_summary",
    ),

    path(
        "students/enrollment-summary/excel/",
        views.enrollment_summary_excel,
        name="enrollment_summary_excel",
    ),

    path(
        "students/enrollment-summary/pdf/",
        views.enrollment_summary_pdf,
        name="enrollment_summary_pdf",
    ),

    # ==========================================================
    # STUDENT STATUS
    # ==========================================================

    path(
        "students/status/",
        views.student_status_report,
        name="student_status_report",
    ),

    # ==========================================================
    # FINANCE
    # ==========================================================

    path(
        "finance/financial-position/",
        views.financial_position,
        name="financial_position",
    ),

    path(
        "finance/financial-transactions/",
        views.financial_transactions,
        name="financial_transactions",
    ),

    path(
        "finance/financial-transactions/excel/",
        views.financial_transactions_excel,
        name="financial_transactions_excel",
    ),

    path(
        "finance/financial-transactions/pdf/",
        views.financial_transactions_pdf,
        name="financial_transactions_pdf",
    ),

    path(
        "finance/outstanding-fees/",
        views.outstanding_fees,
        name="outstanding_fees",
    ),

    path(
        "finance/outstanding-fees/excel/",
        views.outstanding_fees_excel,
        name="outstanding_fees_excel",
    ),

    path(
        "finance/outstanding-fees/pdf/",
        views.outstanding_fees_pdf,
        name="outstanding_fees_pdf",
    ),

    # ==========================================================
    # ACADEMICS
    # ==========================================================

    path(
        "academics/examination-performance/",
        views.examination_performance,
        name="examination_performance",
    ),

    path(
        "academics/examination-performance/excel/",
        views.examination_performance_excel,
        name="examination_performance_excel",
    ),

    path(
        "academics/examination-performance/pdf/",
        views.examination_performance_pdf,
        name="examination_performance_pdf",
    ),

    path(
        "academics/student-result-history/<int:student_id>/",
        views.student_result_history,
        name="student_result_history",
    ),

    path(
        "academics/missing-marks/",
        views.missing_marks,
        name="missing_marks",
    ),

    # ==========================================================
    # SYSTEM
    # ==========================================================

    path(
        "system/user-accounts/",
        views.user_accounts,
        name="user_accounts",
    ),

    path(
        "system/audit-trail/",
        views.audit_trail,
        name="audit_trail",
    ),
]