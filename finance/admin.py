from django.contrib import admin

from .models import (
    FeeCategory,
    FeeStructure,
    FeeStructureItem,
    StudentInvoice,
    InvoiceItem,
    Payment,
    Receipt,
    FinanceSetting,
)
#register your models here

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "is_active",
    )

    search_fields = (
        "code",
    )

    list_filter = (
        "is_active",
    )


class FeeStructureItemInline(admin.TabularInline):

    model = FeeStructureItem
    extra = 1


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        "programme_level",
        "academic_year",
        "semester",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "semester",
        "is_active",
    )

    search_fields = (
        "programme_level__programme__name",
        "programme_level__programme__code",
    )

    


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "invoice",
        "amount",
        "payment_method",
        "reference_number",
        "payment_date",
        "received_by",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "reference_number",
    )


class InvoiceItemInline(
    admin.TabularInline
):
    model = InvoiceItem
    extra = 0

@admin.register(StudentInvoice)
class StudentInvoiceAdmin(
    admin.ModelAdmin
):

    list_display = (
        "invoice_number",
        "student",
        "invoice_date",
        "total_amount",
        "amount_paid",
        "balance",
        "payment_percentage",
        "status",
    )

    list_filter = (
        "status",
        "invoice_date",
    )

    search_fields = (
        "invoice_number",
        "student__admission_no",
        "student__first_name",
        "student__last_name",
    )

    inlines = [
        InvoiceItemInline
    ]

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):

    list_display = (
        "receipt_number",
        "payment",
        "receipt_date",
        "created_by",
    )

    search_fields = (
        "receipt_number",
    )

@admin.register(FinanceSetting)
class FinanceSettingAdmin(admin.ModelAdmin):

    list_display = (
        "minimum_registration_percentage",
        "minimum_exam_percentage",
        "minimum_result_slip_percentage",
        "minimum_transcript_percentage",
        "minimum_graduation_percentage",
        "allow_overpayment",
    )