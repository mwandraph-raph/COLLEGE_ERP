from django.db.models.signals import (
    post_save,
    post_delete,
)
from django.dispatch import receiver

from students.models import SemesterEnrollment

from finance.models import (
    InvoiceItem,
    Payment,
)

from finance.services import (
    recalculate_invoice,
    generate_student_invoice,
)

# ==========================================================
# ENROLLMENT → AUTO CREATE INVOICE
# ==========================================================

@receiver(
    post_save,
    sender=SemesterEnrollment,
)
def create_invoice_on_enrollment(
    sender,
    instance,
    created,
    **kwargs,
):

    if created:
        generate_student_invoice(instance)


# ==========================================================
# INVOICE ITEM CHANGES
# ==========================================================

@receiver(
    post_save,
    sender=InvoiceItem,
)
def update_invoice_after_item_save(
    sender,
    instance,
    **kwargs,
):
    recalculate_invoice(instance.invoice)


@receiver(
    post_delete,
    sender=InvoiceItem,
)
def update_invoice_after_item_delete(
    sender,
    instance,
    **kwargs,
):
    recalculate_invoice(
    instance.invoice
)


# ==========================================================
# PAYMENT CHANGES
# ==========================================================

@receiver(
    post_save,
    sender=Payment,
)
def update_invoice_after_payment_save(
    sender,
    instance,
    **kwargs,
):
    recalculate_invoice(
    instance.invoice
)


@receiver(
    post_delete,
    sender=Payment,
)
def update_invoice_after_payment_delete(
    sender,
    instance,
    **kwargs,
):
    recalculate_invoice(
    instance.invoice
)