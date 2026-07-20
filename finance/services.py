from finance.models import (
    FeeStructure,
    StudentInvoice,
    InvoiceItem,
    FinanceSetting,
    FinancialClearance,
    StudentCredit
)

def generate_student_invoice(enrollment):
    """
    Generate student invoice from
    the matching fee structure.
    """

    # Prevent duplicate invoices
    if hasattr(
        enrollment,
        "invoice"
    ):
        return enrollment.invoice

    try:
        fee_structure = FeeStructure.objects.get(
            programme=enrollment.student.programme,
            academic_year=enrollment.academic_year,
            semester=enrollment.semester,
            study_level=enrollment.study_level,
            is_active=True,
        )

    except FeeStructure.DoesNotExist:

        raise ValueError(
            f"No active fee structure found for "
            f"{enrollment.student.programme} - "
            f"{enrollment.semester} - "
            f"{enrollment.study_level}"
        )
    invoice = StudentInvoice.objects.create(
        student=enrollment.student,
        enrollment=enrollment,
    )

    for item in fee_structure.items.all():

        InvoiceItem.objects.create(
            invoice=invoice,
            fee_category=item.fee_category,
            amount=item.amount,
        )

    # Apply available student credit
    apply_credit_to_invoice(invoice)

    return invoice

def apply_credit_to_invoice(invoice):

    student = invoice.student

    credits = (
        StudentCredit.objects
        .filter(
            student=student
        )
        .order_by(
            "created_at"
        )
    )

    remaining_invoice_amount = invoice.total_amount

    total_credit_applied = 0

    for credit in credits:

        available = credit.balance

        if available <= 0:
            continue

        if remaining_invoice_amount <= 0:
            break

        amount_to_use = min(
            available,
            remaining_invoice_amount
        )

        credit.used_amount += amount_to_use
        credit.save()

        total_credit_applied += amount_to_use
        remaining_invoice_amount -= amount_to_use

    if total_credit_applied > 0:

        invoice.credit_applied = (
            total_credit_applied
        )

        invoice.save()

def update_financial_clearance(
    enrollment,
    user
):

    invoice = enrollment.invoice

    percentage = (
        invoice.payment_percentage
    )

    settings = (
        FinanceSetting.objects.first()
    )

    if not settings:
        return None

    clearance, created = (
        FinancialClearance.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                "updated_by": user
            }
        )
    )

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

    clearance.updated_by = user

    clearance.save()

    return clearance