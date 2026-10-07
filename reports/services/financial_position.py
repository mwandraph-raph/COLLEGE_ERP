"""
XORADEX EDUCORE ERP
FINANCIAL POSITION REPORT SERVICE

Provides role-aware financial position summaries.
"""

from decimal import Decimal

from django.db.models import Sum

from finance.models import StudentInvoice, Payment, StudentCredit


def get_financial_position_students(user):
    """
    Return invoices visible to the current user.

    HOD users are restricted to students belonging
    to their department.
    """

    invoices = StudentInvoice.objects.select_related(
        "student",
        "enrollment",
        "student__programme",
        "student__programme__course",
        "student__programme__course__department",
    )

    if user.groups.filter(name="HOD").exists():
        invoices = invoices.filter(
            student__programme__course__department__hod=user
        )

    return invoices


def get_financial_position_summary(user):
    """
    Build the Financial Position summary.

    Financial Position includes:

    - Expected Revenue
    - Collections
    - Credits
    - Outstanding Balance
    - Invoice count
    """

    invoices = get_financial_position_students(user)

    expected_revenue = (
        invoices.aggregate(
            total=Sum("invoice_total")
        )["total"]
        or Decimal("0.00")
    )

    outstanding_balance = (
        invoices.aggregate(
            total=Sum("balance_cached")
        )["total"]
        or Decimal("0.00")
    )

    amount_paid = (
        invoices.aggregate(
            total=Sum("amount_paid_cached")
        )["total"]
        or Decimal("0.00")
    )

    credit_applied = (
        invoices.aggregate(
            total=Sum("credit_applied")
        )["total"]
        or Decimal("0.00")
    )

    # Payments belonging to the visible invoices.
    payments = Payment.objects.filter(
        invoice__in=invoices,
        posting_status="POSTED",
        is_reversed=False,
    )

    collections = (
        payments.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # Credits belonging to students visible to this user.
    student_ids = invoices.values_list(
        "student_id",
        flat=True,
    ).distinct()

    credits = (
        StudentCredit.objects.filter(
            student_id__in=student_ids,
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    credits_used = (
        StudentCredit.objects.filter(
            student_id__in=student_ids,
        ).aggregate(
            total=Sum("used_amount")
        )["total"]
        or Decimal("0.00")
    )

    return {
        "invoice_count": invoices.count(),
        "expected_revenue": expected_revenue,
        "collections": collections,
        "amount_paid": amount_paid,
        "credits": credits,
        "credits_used": credits_used,
        "credit_applied": credit_applied,
        "outstanding_balance": outstanding_balance,
    }