
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from students.models import (
    Student,
    AcademicYear,
)
# Create your models here.

User = get_user_model()

class Graduation(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ELIGIBLE", "Eligible"),
        ("APPROVED", "Approved"),
        ("GRADUATED", "Graduated"),
    ]

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="graduation",
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="graduations",
    )

    graduation_date = models.DateField(
        default=timezone.now,
    )

    certificate_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_graduations",
    )

    approved_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-graduation_date",
            "student__admission_no",
        ]
        verbose_name = "Graduation"
        verbose_name_plural = "Graduations"

    def __str__(self):
        return (
            f"{self.student} - {self.certificate_number}"
        )

    def save(self, *args, **kwargs):
        """
        Automatically generate certificate number.

        Example:
        CERT/2027/00001
        """

        if not self.certificate_number:

            year = self.graduation_date.year
            prefix = f"CERT/{year}/"

            last_record = (
                Graduation.objects.filter(
                    certificate_number__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            if last_record:
                try:
                    last_number = int(
                        last_record.certificate_number.split("/")[-1]
                    )
                except (
                    ValueError,
                    IndexError,
                    AttributeError,
                ):
                    last_number = 0
            else:
                last_number = 0

            self.certificate_number = (
                f"{prefix}{last_number + 1:05d}"
            )

        super().save(*args, **kwargs)