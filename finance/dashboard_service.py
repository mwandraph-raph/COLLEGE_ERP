from datetime import date, timedelta
from decimal import Decimal
import json

from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce, ExtractMonth

from finance.models import (
    StudentInvoice,
    Payment,
    Receipt,
    StudentCredit,
)

from students.models import (
    AcademicYear,
    Semester,
)


# ==========================================================
# CONSTANTS
# ==========================================================

ZERO = Decimal("0.00")


# ==========================================================
# MONEY SUM HELPER
# ==========================================================

def money_sum(queryset, field="amount"):
    """
    Safely calculate a Decimal sum.

    Returns Decimal("0.00") when there are no records.
    """

    return (
        queryset.aggregate(
            total=Coalesce(
                Sum(field),
                ZERO,
                output_field=DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            )
        )["total"]
        or ZERO
    )


# ==========================================================
# FINANCE DASHBOARD DATA
# ==========================================================

def get_finance_dashboard_data():
    """
    Central source of financial dashboard statistics.

    Financial rules:

    1. Only POSTED and non-reversed payments count as
       collections.

    2. Only POSTED invoices count as active obligations.

    3. Invoice balances come from balance_cached.

    4. Previous student credit used during the active
       academic period is included in settlement value.

    5. Outstanding balance comes from balance_cached.

    6. Dashboard invoice figures are restricted to the
       active academic year and active semester.

    7. Collections are based on payments belonging to
       invoices in the active academic period.
    """

    today = date.today()

    # ======================================================
    # DATE RANGES
    # ======================================================

    start_of_week = today - timedelta(
        days=today.weekday()
    )

    start_of_month = today.replace(
        day=1
    )

    # ======================================================
    # ACTIVE ACADEMIC YEAR
    # ======================================================

    active_academic_year = (
        AcademicYear.objects
        .filter(
            is_active=True
        )
        .first()
    )

    # ======================================================
    # ACTIVE SEMESTER
    # ======================================================

    active_semester = None

    if active_academic_year:

        active_semester = (
            Semester.objects
            .filter(
                academic_year=active_academic_year,
                is_active=True,
            )
            .first()
        )

    # ======================================================
    # POSTED PAYMENTS
    # ======================================================

    posted_payments = (
        Payment.objects
        .filter(
            posting_status="POSTED",
            is_reversed=False,
        )
    )

    # ======================================================
    # SESSION PAYMENTS
    # ======================================================

    session_payments = posted_payments

    if active_academic_year:

        session_payments = session_payments.filter(
            invoice__enrollment__academic_year=(
                active_academic_year
            )
        )

    if active_semester:

        session_payments = session_payments.filter(
            invoice__enrollment__semester=(
                active_semester
            )
        )

    # ======================================================
    # POSTED INVOICES
    # ======================================================

    posted_invoices = (
        StudentInvoice.objects
        .filter(
            status="POSTED"
        )
    )

    # ======================================================
    # SESSION INVOICES
    # ======================================================

    session_invoices = posted_invoices

    if active_academic_year:

        session_invoices = session_invoices.filter(
            enrollment__academic_year=(
                active_academic_year
            )
        )

    if active_semester:

        session_invoices = session_invoices.filter(
            enrollment__semester=(
                active_semester
            )
        )

    # ======================================================
    # COLLECTIONS
    # ======================================================

    total_collected = money_sum(
        session_payments
    )

    today_collections = money_sum(
        session_payments.filter(
            payment_date=today
        )
    )

    week_collections = money_sum(
        session_payments.filter(
            payment_date__gte=start_of_week
        )
    )

    month_collections = money_sum(
        session_payments.filter(
            payment_date__gte=start_of_month
        )
    )

    # ======================================================
    # GROSS INVOICED
    # ======================================================

    gross_invoiced = money_sum(
        session_invoices,
        "invoice_total"
    )

    # ======================================================
    # PREVIOUS CREDIT APPLIED
    #
    # IMPORTANT:
    #
    # The actual credit usage is stored in:
    #
    #     StudentCredit.used_amount
    #
    # Therefore we do NOT rely only on:
    #
    #     StudentInvoice.credit_applied
    #
    # This allows the dashboard to read the actual credit
    # usage recorded against students' credit accounts.
    # ======================================================

    session_student_ids = (
        session_invoices
        .values_list(
            "student_id",
            flat=True
        )
        .distinct()
    )

    credits_applied = money_sum(
        StudentCredit.objects.filter(
            student_id__in=session_student_ids,
            used_amount__gt=ZERO,
        ),
        "used_amount"
    )

    if credits_applied < ZERO:
        credits_applied = ZERO

    # ======================================================
    # SETTLED VALUE
    #
    # Current cash + previous credit used.
    #
    # Example:
    #
    # Cash payment       25,000
    # Previous credit     1,000
    # ---------------------------
    # Settled value      26,000
    # ======================================================

    settled_value = (
        total_collected
        + credits_applied
    )

    # ======================================================
    # OUTSTANDING BALANCE
    #
    # Use the cached invoice balance because it already
    # accounts for payments and credits.
    # ======================================================

    outstanding_balance = money_sum(
        session_invoices,
        "balance_cached"
    )

    if outstanding_balance < ZERO:
        outstanding_balance = ZERO

    # ======================================================
    # COLLECTION / SETTLEMENT RATE
    # ======================================================

    if gross_invoiced > ZERO:

        collection_rate = round(
            (
                settled_value
                / gross_invoiced
            ) * Decimal("100"),
            2,
        )

        collection_rate = min(
            collection_rate,
            Decimal("100.00")
        )

    else:

        collection_rate = ZERO

    # ======================================================
    # PENDING INVOICES
    # ======================================================

    pending_invoices = (
        session_invoices
        .filter(
            balance_cached__gt=ZERO
        )
        .count()
    )

    # ======================================================
    # TOTAL INVOICED STUDENTS
    # ======================================================

    total_invoiced_students = (
        session_invoices
        .values(
            "student"
        )
        .distinct()
        .count()
    )

    # ======================================================
    # BILLING STATUS
    # ======================================================

    fully_cleared = (
        session_invoices
        .filter(
            balance_cached__lte=ZERO
        )
        .count()
    )

    partially_paid = (
        session_invoices
        .filter(
            amount_paid_cached__gt=ZERO,
            balance_cached__gt=ZERO,
        )
        .count()
    )

    not_paid = (
        session_invoices
        .filter(
            amount_paid_cached__lte=ZERO,
            balance_cached__gt=ZERO,
        )
        .count()
    )

    # ======================================================
    # RECEIPTS
    # ======================================================

    receipts_issued = Receipt.objects.count()

    # ======================================================
    # REVERSED PAYMENTS
    # ======================================================

    reversed_payments = (
        Payment.objects
        .filter(
            is_reversed=True
        )
        .count()
    )

    # ======================================================
    # PAYMENT METHODS
    # ======================================================

    mpesa_total = money_sum(
        session_payments.filter(
            payment_method="MPESA"
        )
    )

    bank_total = money_sum(
        session_payments.filter(
            payment_method="BANK"
        )
    )

    cash_total = money_sum(
        session_payments.filter(
            payment_method="CASH"
        )
    )

    # ======================================================
    # OTHER PAYMENTS
    # ======================================================

    categorized_total = (
        mpesa_total
        + bank_total
        + cash_total
    )

    other_total = max(
        ZERO,
        total_collected - categorized_total
    )

    # ======================================================
    # PAYMENT METHOD SHARES
    # ======================================================

    if total_collected > ZERO:

        mpesa_share = round(
            (
                mpesa_total
                / total_collected
            ) * Decimal("100")
        )

        bank_share = round(
            (
                bank_total
                / total_collected
            ) * Decimal("100")
        )

        cash_share = round(
            (
                cash_total
                / total_collected
            ) * Decimal("100")
        )

        other_share = max(
            0,
            100
            - mpesa_share
            - bank_share
            - cash_share,
        )

    else:

        mpesa_share = 0
        bank_share = 0
        cash_share = 0
        other_share = 0

    # ======================================================
    # PROJECTED CASH FLOW
    # ======================================================

    projected_cash_flow = outstanding_balance

    # ======================================================
    # BANK COLLECTIONS
    # ======================================================

    bank_reconciled = bank_total

    # ======================================================
    # MONTHLY REVENUE TREND
    # ======================================================

    monthly = (
        session_payments
        .annotate(
            month=ExtractMonth(
                "payment_date"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Sum("amount")
        )
        .order_by(
            "month"
        )
    )

    month_names = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    revenue_labels = [
        month_names[item["month"]]
        for item in monthly
        if item["month"] is not None
    ]

    revenue_values = [
        float(
            item["total"] or ZERO
        )
        for item in monthly
    ]

    # ======================================================
    # PAYMENT METHOD CHART
    # ======================================================

    category_labels = [
        "M-Pesa",
        "Bank",
        "Cash",
    ]

    category_values = [
        float(mpesa_total),
        float(bank_total),
        float(cash_total),
    ]

    # ======================================================
    # RETURN DASHBOARD CONTEXT
    # ======================================================

    return {

        # ==================================================
        # ACTIVE PERIOD
        # ==================================================

        "active_academic_year": active_academic_year,
        "active_semester": active_semester,

        # ==================================================
        # COLLECTIONS
        # ==================================================

        "total_collected": total_collected,
        "total_fees_collected": total_collected,

        "today_collections": today_collections,
        "todays_collections": today_collections,

        "week_collections": week_collections,
        "weekly_collections": week_collections,

        "month_collections": month_collections,
        "monthly_collections": month_collections,

        # ==================================================
        # INVOICING
        # ==================================================

        "gross_invoiced": gross_invoiced,
        "expected_revenue": gross_invoiced,

        # ==================================================
        # CREDIT
        # ==================================================

        "credits_applied": credits_applied,

        # ==================================================
        # SETTLEMENT
        # ==================================================

        "settled_value": settled_value,
        "collection_rate": collection_rate,

        # ==================================================
        # BALANCES
        # ==================================================

        "outstanding_balance": outstanding_balance,
        "outstanding_balances": outstanding_balance,

        "pending_invoices": pending_invoices,

        # ==================================================
        # PROJECTED CASH
        # ==================================================

        "projected_cash_flow": projected_cash_flow,

        # ==================================================
        # STUDENTS
        # ==================================================

        "total_invoiced_students": total_invoiced_students,

        # ==================================================
        # BILLING STATUS
        # ==================================================

        "fully_cleared": fully_cleared,

        "partially_paid": partially_paid,
        "partially_cleared": partially_paid,

        "not_paid": not_paid,
        "not_cleared": not_paid,

        # ==================================================
        # RECEIPTS
        # ==================================================

        "receipts_issued": receipts_issued,

        "reversed_payments": reversed_payments,

        # ==================================================
        # PAYMENT METHODS
        # ==================================================

        "mpesa_total": mpesa_total,
        "bank_total": bank_total,
        "cash_total": cash_total,
        "other_total": other_total,

        "bank_reconciled": bank_reconciled,

        # ==================================================
        # PAYMENT SHARES
        # ==================================================

        "mpesa_share": mpesa_share,
        "bank_share": bank_share,
        "cash_share": cash_share,
        "other_share": other_share,

        # ==================================================
        # CHART DATA
        # ==================================================

        "revenue_labels": json.dumps(
            revenue_labels
        ),

        "revenue_values": json.dumps(
            revenue_values
        ),

        "category_labels": json.dumps(
            category_labels
        ),

        "category_values": json.dumps(
            category_values
        ),
    }