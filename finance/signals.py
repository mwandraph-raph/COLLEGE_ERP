from django.db.models.signals import post_save
from django.dispatch import receiver

from students.models import (
    SemesterEnrollment,
)

from finance.services import (
    generate_student_invoice,
)

@receiver(
    post_save,
    sender=SemesterEnrollment
)
def create_invoice_on_enrollment(
    sender,
    instance,
    created,
    **kwargs
):

    if created:

        generate_student_invoice(
            instance
        )

