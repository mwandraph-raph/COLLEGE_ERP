from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from finance.models import (
    FeeStructure,
    StudentInvoice,
    InvoiceItem,
    FinanceSetting,
    FinancialClearance,
    StudentCredit,
)


# ==========================================================
# RECALCULATE INVOICE TOTALS
# ==========================================================

@transaction.atomic
def recalculate_invoice(invoice):

    invoice_total = (
        invoice.items.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    amount_paid = (
        invoice.payments.filter(
            posting_status="POSTED",
            is_reversed=False,
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    balance = (
        invoice_total
        - invoice.credit_applied
        - amount_paid
    )

    StudentInvoice.objects.filter(
        pk=invoice.pk
    ).update(
        invoice_total=invoice_total,
        amount_paid_cached=amount_paid,
        balance_cached=balance,
    )

    invoice.invoice_total = invoice_total
    invoice.amount_paid_cached = amount_paid
    invoice.balance_cached = balance

    return invoice


# ==========================================================
# GENERATE STUDENT INVOICE
# ==========================================================

@transaction.atomic
def generate_student_invoice(enrollment):

    existing_invoice = getattr(
        enrollment,
        "invoice",
        None,
    )

    if existing_invoice:

        apply_credit_to_invoice(
            existing_invoice
        )

        recalculate_invoice(
            existing_invoice
        )

        update_financial_clearance(
            enrollment
        )

        return existing_invoice

    try:
        fee_structure = (
            FeeStructure.objects
            .select_related(
                "programme_level",
                "academic_year",
                "semester",
            )
            .prefetch_related(
                "items",
                "items__fee_category",
            )
            .get(
                programme_level=enrollment.programme_level,
                academic_year=enrollment.academic_year,
                semester=enrollment.semester,
                is_active=True,
            )
        )

    except FeeStructure.DoesNotExist:

        raise ValueError(
            "No active fee structure found for "
            f"{enrollment.programme_level} | "
            f"{enrollment.academic_year} | "
            f"{enrollment.semester}"
        )

    invoice = StudentInvoice.objects.create(
        student=enrollment.student,
        enrollment=enrollment,
        status="POSTED",
    )

    InvoiceItem.objects.bulk_create([
        InvoiceItem(
            invoice=invoice,
            fee_category=item.fee_category,
            amount=item.amount,
        )
        for item in fee_structure.items.all()
    ])

    recalculate_invoice(invoice)

    apply_credit_to_invoice(invoice)

    recalculate_invoice(invoice)

    update_financial_clearance(enrollment)

    return invoice


# ==========================================================
# APPLY STUDENT CREDIT
# ==========================================================

@transaction.atomic
def apply_credit_to_invoice(invoice):

    recalculate_invoice(invoice)

    remaining_balance = invoice.balance_cached

    if remaining_balance <= Decimal("0.00"):
        return Decimal("0.00")

    credits = (
        StudentCredit.objects
        .select_related("source_payment")
        .filter(
            student=invoice.student,
            source_payment__posting_status="POSTED",
            source_payment__is_reversed=False,
        )
        .order_by(
            "created_at",
            "id",
        )
    )

    credit_used = Decimal("0.00")

    for credit in credits:

        if remaining_balance <= Decimal("0.00"):
            break

        available = credit.balance

        if available <= Decimal("0.00"):
            continue

        amount_to_apply = min(
            available,
            remaining_balance,
        )

        credit.used_amount += amount_to_apply

        credit.save(
            update_fields=["used_amount"]
        )

        credit_used += amount_to_apply
        remaining_balance -= amount_to_apply

    if credit_used > Decimal("0.00"):

        invoice.credit_applied += credit_used

        invoice.save(
            update_fields=["credit_applied"]
        )

        recalculate_invoice(invoice)

    return credit_used


# ==========================================================
# UPDATE FINANCIAL CLEARANCE
# ==========================================================

@transaction.atomic
def update_financial_clearance(
    enrollment,
    user=None,
):

    if not hasattr(
        enrollment,
        "invoice",
    ):
        return None

    invoice = enrollment.invoice

    recalculate_invoice(invoice)

    settings = FinanceSetting.objects.first()

    if settings is None:
        return None

    clearance, created = (
        FinancialClearance.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                "updated_by": user,
            },
        )
    )

    percentage = invoice.payment_percentage

    clearance.registration_cleared = (
        percentage >=
        settings.minimum_registration_percentage
    )

    clearance.exam_cleared = (
        percentage >=
        settings.minimum_exam_percentage
    )

    clearance.result_slip_cleared = (
        percentage >=
        settings.minimum_result_slip_percentage
    )

    clearance.transcript_cleared = (
        percentage >=
        settings.minimum_transcript_percentage
    )

    clearance.graduation_cleared = (
        percentage >=
        settings.minimum_graduation_percentage
    )

    if user is not None:
        clearance.updated_by = user

    clearance.save()

    return clearance