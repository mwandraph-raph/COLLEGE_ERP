from finance.models import (
    FeeStructure,
    StudentInvoice,
    InvoiceItem,
    FinanceSetting,
    FinancialClearance,
    StudentCredit,
)
from django.db import transaction

@transaction.atomic
def generate_student_invoice(enrollment):
    """
    Generate a student invoice from a semester enrollment.

    The function is idempotent:
        • Returns the existing invoice if one already exists.
        • Otherwise creates a new invoice.
        • Generates all invoice items.
        • Applies available credits.
        • Updates financial clearance.

    Parameters
    ----------
    enrollment : SemesterEnrollment

    Returns
    -------
    StudentInvoice
    """

    # ==========================================================
    # Return existing invoice (Prevent duplicates)
    # ==========================================================

    existing_invoice = getattr(
        enrollment,
        "invoice",
        None,
    )

    if existing_invoice:
        return existing_invoice

    # ==========================================================
    # Retrieve Active Fee Structure
    # ==========================================================

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
            f"{enrollment.semester}."
        )

    # ==========================================================
    # Create Invoice
    # ==========================================================

    invoice = StudentInvoice.objects.create(

        student=enrollment.student,

        enrollment=enrollment,

        status=StudentInvoice.POSTED,

    )

    # ==========================================================
    # Create Invoice Items
    # ==========================================================

    invoice_items = [

        InvoiceItem(

            invoice=invoice,

            fee_category=item.fee_category,

            amount=item.amount,

        )

        for item in fee_structure.items.all()

    ]

    InvoiceItem.objects.bulk_create(
        invoice_items
    )

    # ==========================================================
    # Apply Student Credits
    # ==========================================================

    apply_credit_to_invoice(
        invoice
    )

    # ==========================================================
    # Update Financial Clearance
    # ==========================================================

    update_financial_clearance(
        enrollment
    )

    return invoice





def apply_credit_to_invoice(invoice):

    """
    Automatically use available student credit.
    """


    credits = (

        StudentCredit.objects

        .filter(

            student=invoice.student

        )

        .order_by(

            "created_at"

        )

    )


    remaining_amount = invoice.total_amount

    credit_used = 0



    for credit in credits:


        available = credit.balance


        if available <= 0:

            continue



        if remaining_amount <= 0:

            break



        amount = min(

            available,

            remaining_amount

        )


        credit.used_amount += amount

        credit.save()


        credit_used += amount

        remaining_amount -= amount



    if credit_used > 0:


        invoice.credit_applied = credit_used

        invoice.save()





def update_financial_clearance(enrollment, user=None):

    """
    Automatically update financial clearance
    based on invoice payment percentage.
    """


    if not hasattr(enrollment, "invoice"):

        return None



    invoice = enrollment.invoice


    settings = FinanceSetting.objects.first()


    if not settings:

        return None



    clearance, created = FinancialClearance.objects.get_or_create(

        enrollment=enrollment,

        defaults={

            "updated_by": user

        }

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



    # Only update user if provided
    if user is not None:

        clearance.updated_by = user

    clearance.save()

    return clearance


