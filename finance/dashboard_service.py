from datetime import date, timedelta
from django.db.models.functions import ExtractMonth
import json
from django.db.models import (
    Sum,
    Count,
    Q,
    DecimalField,
)
from django.db.models.functions import Coalesce

from finance.models import (
    StudentInvoice,
    Payment,
    Receipt,
)


def get_finance_dashboard_data():
    """
    Finance Dashboard KPIs.

    This is the ONLY place where dashboard
    statistics are calculated.
    """

    today = date.today()

    start_of_week = today - timedelta(days=today.weekday())

    start_of_month = today.replace(day=1)

    # ======================================================
    # COLLECTIONS
    # ======================================================

    total_collected = (
        Payment.objects.filter(
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    today_collections = (
        Payment.objects.filter(
            payment_date=today,
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    week_collections = (
        Payment.objects.filter(
            payment_date__gte=start_of_week,
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    month_collections = (
        Payment.objects.filter(
            payment_date__gte=start_of_month,
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    # ======================================================
    # INVOICES
    # ======================================================

    expected_revenue = (
        StudentInvoice.objects.aggregate(
            total=Coalesce(
                Sum("invoice_total"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    outstanding_balance = (
        StudentInvoice.objects.aggregate(
            total=Coalesce(
                Sum("balance_cached"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    pending_invoices = (
        StudentInvoice.objects.filter(
            balance_cached__gt=0
        ).count()
    )


    total_invoiced_students = (
        StudentInvoice.objects
        .filter(
            status="POSTED"
        )
        .values(
            "student"
        )
        .distinct()
        .count()
    )
    # ======================================================
    # BILLING SUMMARY
    # ======================================================

    fully_cleared = (
        StudentInvoice.objects.filter(
            balance_cached=0
        ).count()
    )

    partially_paid = (
        StudentInvoice.objects.filter(
            amount_paid_cached__gt=0,
            balance_cached__gt=0,
        ).count()
    )

    not_paid = (
        StudentInvoice.objects.filter(
            amount_paid_cached=0
        ).count()
    )

    # ======================================================
    # RECEIPTS
    # ======================================================

    receipts_issued = Receipt.objects.count()

    reversed_payments = (
        Payment.objects.filter(
            is_reversed=True
        ).count()
    )

    # ======================================================
    # PAYMENT METHODS
    # ======================================================

    mpesa_total = (
        Payment.objects.filter(
            payment_method="MPESA",
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )


    bank_total = (
        Payment.objects.filter(
            payment_method="BANK",
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    cash_total = (
        Payment.objects.filter(
            payment_method="CASH",
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Coalesce(
                Sum("amount"),
                0,
                output_field=DecimalField(),
            )
        )["total"]
    )

    # ======================================================
    # PAYMENT METHOD PERCENTAGES
    # ======================================================

    if total_collected > 0:

        mpesa_share = round((mpesa_total / total_collected) * 100)

        bank_share = round((bank_total / total_collected) * 100)

        cash_share = round((cash_total / total_collected) * 100)

    else:

        mpesa_share = 0

        bank_share = 0

        cash_share = 0

    other_share = max(
        0,
        100 - mpesa_share - bank_share - cash_share,
    )


    # ======================================================
    # MONTHLY REVENUE TREND
    # ======================================================

    monthly = (
        Payment.objects.filter(
            posting_status="POSTED",
            is_reversed=False,
        )
        .annotate(month=ExtractMonth("payment_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
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
    ]

    revenue_values = [
        float(item["total"])
        for item in monthly
    ]

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
    # RETURN CONTEXT
    # ======================================================

    return {

    "total_collected": total_collected,

    "today_collections": today_collections,

    "week_collections": week_collections,

    "month_collections": month_collections,

    "expected_revenue": expected_revenue,

    "outstanding_balance": outstanding_balance,

    "pending_invoices": pending_invoices,
    
    "total_invoiced_students": total_invoiced_students,

    "fully_cleared": fully_cleared,

    "partially_paid": partially_paid,

    "not_paid": not_paid,

    "receipts_issued": receipts_issued,

    "reversed_payments": reversed_payments,

    "mpesa_total": mpesa_total,

    "bank_total": bank_total,

    "cash_total": cash_total,

    "mpesa_share": mpesa_share,

    "bank_share": bank_share,

    "cash_share": cash_share,

    "other_share": other_share,

    "revenue_labels": json.dumps(revenue_labels),
    "revenue_values": json.dumps(revenue_values),

    "category_labels": json.dumps(category_labels),
    "category_values": json.dumps(category_values),

}