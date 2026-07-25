from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from students.models import (
    Programme,
    ProgrammeLevel,
    AcademicYear,
    Semester,
    Student,
    SemesterEnrollment,
)
# Create your models here.
class FeeCategory(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Fee Category"
        verbose_name_plural = "Fee Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class FeeStructure(models.Model):

    programme_level = models.ForeignKey(
        ProgrammeLevel,
        on_delete=models.PROTECT,
        related_name="fee_structures",
        null=True,
        blank=True,
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="fee_structures",
        null=True,
        blank=True,
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="fee_structures",
    )

    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        ordering = [
            "programme_level",
            "academic_year",
            "semester",
        ]

        unique_together = (
            "programme_level",
            "academic_year",
            "semester",
        )


    def save(self, *args, **kwargs):

        if not self.name:

            self.name = (
                f"{self.programme_level} "
                f"{self.academic_year} "
                f"{self.semester}"
            )

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return (
            self.items.aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )

    def __str__(self):

        return self.name

    
class FeeStructureItem(models.Model):

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name="items"
    )

    fee_category = models.ForeignKey(
        FeeCategory,
        on_delete=models.PROTECT
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:

        ordering = [
            "fee_category"
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "fee_structure",
                    "fee_category",
                ],
                name="unique_fee_structure_item"
            )
        ]

    def __str__(self):

        return (
            f"{self.fee_category} "
            f"- {self.amount}"
        )
    
class StudentInvoice(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("POSTED", "Posted"),
        ("CANCELLED", "Cancelled"),
    ]

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    enrollment = models.OneToOneField(
        SemesterEnrollment,
        on_delete=models.CASCADE,
        related_name="invoice"
    )

    invoice_date = models.DateField(
        auto_now_add=True
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    credit_applied = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-invoice_date"
        ]

    @property
    def total_amount(self):

        return sum(
            item.amount
            for item in self.items.all()
        )

    @property
    def amount_paid(self):

        return sum(
            payment.amount
            for payment in self.payments.filter(
                is_reversed=False
            )
        )

    @property
    def balance(self):

        return (
            self.total_amount
            - self.credit_applied
            - self.amount_paid
        )

    @property
    def payment_percentage(self):

        net_amount = (
            self.total_amount
            - self.credit_applied
        )

        if net_amount <= 0:

            return 100

        return round(
            (
                self.amount_paid
                / net_amount
            ) * 100,
            2
        )

    def save(self, *args, **kwargs):

        if not self.invoice_number:

            year = timezone.now().year

            prefix = f"INV/{year}/"

            last_invoice = (
                StudentInvoice.objects
                .filter(
                    invoice_number__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            if last_invoice:

                try:

                    last_number = int(
                        last_invoice.invoice_number
                        .split("/")[-1]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    last_number = 0

            else:

                last_number = 0

            self.invoice_number = (
                f"{prefix}{last_number + 1:05d}"
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return self.invoice_number
    
class InvoiceItem(models.Model):

    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    fee_category = models.ForeignKey(
        FeeCategory,
        on_delete=models.PROTECT
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:

        ordering = [
            "fee_category"
        ]

    def __str__(self):

        return (
            f"{self.fee_category}"
        )
    

class Payment(models.Model):

    PAYMENT_METHODS = [
        ("MPESA", "MPESA"),
        ("BANK", "Bank"),
        ("CASH", "Cash"),
    ]

    POSTING_STATUS = [
        ("POSTED", "Posted"),
        ("REVERSED", "Reversed"),
    ]

    payment_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    invoice = models.ForeignKey(
        StudentInvoice,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    payment_date = models.DateField(
        auto_now_add=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
    )

    reference_number = models.CharField(
        max_length=100,
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    remarks = models.TextField(
        blank=True,
    )

    posting_status = models.CharField(
        max_length=20,
        choices=POSTING_STATUS,
        default="POSTED",
    )

    is_reversed = models.BooleanField(
        default=False,
    )

    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reversed_payments",
    )

    reversal_reason = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-payment_date",
            "-id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "invoice",
                    "reference_number",
                ],
                name="unique_invoice_payment_reference",
            )
        ]

    def save(self, *args, **kwargs):

        # Prevent duplicate payment reference
        if Payment.objects.filter(
            invoice=self.invoice,
            reference_number=self.reference_number,
        ).exclude(
            pk=self.pk,
        ).exists():

            raise ValidationError(
                "This payment reference has already been recorded."
            )

        # Generate payment number
        if not self.payment_number:

            year = timezone.now().year

            prefix = f"PAY/{year}/"

            last_payment = (
                Payment.objects.filter(
                    payment_number__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            last_number = 0

            if last_payment:

                try:

                    last_number = int(
                        last_payment.payment_number.split("/")[-1]
                    )

                except (ValueError, IndexError):

                    last_number = 0

            self.payment_number = (
                f"{prefix}{last_number + 1:05d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.payment_number

class StudentCredit(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="credits"
    )

    source_payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="credit"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    used_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    @property
    def balance(self):

        return (
            self.amount -
            self.used_amount
        )


    def __str__(self):

        return (
            f"{self.student} "
            f"- Credit {self.balance}"
        )


class Receipt(models.Model):

    receipt_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="receipt"
    )

    receipt_date = models.DateField(
        auto_now_add=True
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="receipts_created"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            "-receipt_date",
            "-id",
        ]

    def save(self, *args, **kwargs):

        if not self.receipt_number:

            year = timezone.now().year

            prefix = f"RCT/{year}/"

            last_receipt = (
                Receipt.objects
                .filter(
                    receipt_number__startswith=prefix
                )
                .order_by("-id")
                .first()
            )

            if last_receipt:

                try:

                    last_number = int(
                        last_receipt.receipt_number
                        .split("/")[-1]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    last_number = 0

            else:

                last_number = 0

            self.receipt_number = (
                f"{prefix}{last_number + 1:05d}"
            )

        super().save(
            *args,
            **kwargs
        )

    def __str__(self):

        return self.receipt_number
    

class FinanceSetting(models.Model):

    minimum_registration_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00
    )

    minimum_exam_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00
    )

    minimum_result_slip_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00
    )

    minimum_transcript_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00
    )

    minimum_graduation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00
    )

    allow_overpayment = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = "Finance Setting"
        verbose_name_plural = "Finance Settings"
        
    def save(self, *args, **kwargs):

        if not self.pk and FinanceSetting.objects.exists():

            raise ValueError(
                "Only one Finance Setting record is allowed."
            )

        super().save(
            *args,
            **kwargs
        )
    def __str__(self):

        return "Finance Settings"
    

class FinancialClearance(models.Model):

    enrollment = models.OneToOneField(
        SemesterEnrollment,
        on_delete=models.CASCADE,
        related_name="financial_clearance"
    )

    registration_cleared = models.BooleanField(
        default=False
    )

    exam_cleared = models.BooleanField(
        default=False
    )

    result_slip_cleared = models.BooleanField(
        default=False
    )

    transcript_cleared = models.BooleanField(
        default=False
    )

    graduation_cleared = models.BooleanField(
        default=False
    )

    remarks = models.TextField(
        blank=True
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-updated_at"
        ]

    def __str__(self):

        return str(
            self.enrollment.student
        )