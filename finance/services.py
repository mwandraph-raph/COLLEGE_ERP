from finance.models import (
    FeeStructure,
    StudentInvoice,
    InvoiceItem,
    FinanceSetting,
    FinancialClearance,
    StudentCredit,
)


def generate_student_invoice(enrollment):
    """
    Generate invoice automatically
    from the student's semester enrollment.
    """

    # Prevent duplicate invoice
    if hasattr(enrollment, "invoice"):

        return enrollment.invoice


    try:

        fee_structure = FeeStructure.objects.get(

            programme_level=enrollment.programme_level,

            academic_year=enrollment.academic_year,

            semester=enrollment.semester,

            is_active=True,

        )


    except FeeStructure.DoesNotExist:

        raise ValueError(

            "No active fee structure found for "
            f"{enrollment.programme_level} - "
            f"{enrollment.academic_year} - "
            f"{enrollment.semester}"

        )


    invoice = StudentInvoice.objects.create(

        student=enrollment.student,

        enrollment=enrollment,

        status="POSTED",

    )


    for item in fee_structure.items.all():


        InvoiceItem.objects.create(

            invoice=invoice,

            fee_category=item.fee_category,

            amount=item.amount,

        )


    apply_credit_to_invoice(invoice)


    # Create/update financial clearance
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