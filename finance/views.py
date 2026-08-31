from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.db import transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from finance.services import (
    recalculate_invoice,
    update_financial_clearance,
)
from decimal import Decimal
from students.models import SemesterEnrollment, AcademicYear, Semester
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    FeeCategory,
    FeeStructure,
    FeeStructureItem,
    StudentInvoice,
    InvoiceItem,
    Payment,
    Receipt,
    FinanceSetting,
    Student,
    FinancialClearance,
    StudentCredit,
    )
from .forms import (
    FeeCategoryForm,
    FeeStructureForm,
    FeeStructureItemForm,
    PaymentForm,
    ReversePaymentForm,
    FinanceSettingForm,
    PaymentReversalForm
    )

from .dashboard_service import get_finance_dashboard_data
# Create your views here.

@login_required
def finance_dashboard(request):

    context = get_finance_dashboard_data()

    return render(
        request,
        "students/dashboards/finance_home.html",
        context
    )

@login_required
def fee_category_list(request):

    categories = FeeCategory.objects.all()

    return render(
        request,
        "finance/fee_categories/list.html",
        {
            "categories": categories
        }
    )

@login_required
def fee_category_create(request):

    if request.method == "POST":

        form = FeeCategoryForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm()

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form
        }
    )

@login_required
def fee_category_update(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk
    )

    if request.method == "POST":

        form = FeeCategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm(
            instance=category
        )

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form
        }
    )

@login_required
def fee_category_delete(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk
    )

    if request.method == "POST":

        category.delete()

        return redirect(
            "finance:fee_category_list"
        )

    return render(
        request,
        "finance/fee_categories/delete.html",
        {
            "category": category
        }
    )

@login_required
def fee_structure_list(request):

    fee_structures = (
        FeeStructure.objects
        .select_related(
        "programme_level",
        "academic_year",
        "semester",
        )
    )

    return render(
        request,
        "finance/fee_structures/list.html",
        {
            "fee_structures": fee_structures
        }
    )

@login_required
def fee_structure_create(request):

    if request.method == "POST":

        form = FeeStructureForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_structure_list"
            )

    else:

        form = FeeStructureForm()

    return render(
        request,
        "finance/fee_structures/form.html",
        {
            "form": form
        }
    )

@login_required
def fee_structure_detail(request, pk):

    structure = get_object_or_404(
        FeeStructure,
        pk=pk
    )

    items = (
        structure.items
        .select_related(
            "fee_category"
        )
    )

    return render(
        request,
        "finance/fee_structures/detail.html",
        {
            "structure": structure,
            "items": items,
        }
    )

@login_required
def fee_structure_item_create(request, structure_id):

    structure = get_object_or_404(
        FeeStructure,
        pk=structure_id
    )

    if request.method == "POST":

        form = FeeStructureItemForm(
            request.POST
        )

        if form.is_valid():

            item = form.save(
                commit=False
            )

            item.fee_structure = structure

            item.save()

            return redirect(
                "finance:fee_structure_detail",
                pk=structure.id
            )

    else:

        form = FeeStructureItemForm()

    return render(
        request,
        "finance/fee_structure_items/form.html",
        {
            "form": form,
            "structure": structure,
        }
    )


@login_required
def fee_structure_item_update(request, pk):

    item = get_object_or_404(
        FeeStructureItem,
        pk=pk
    )

    if request.method == "POST":

        form = FeeStructureItemForm(
            request.POST,
            instance=item
        )

        if form.is_valid():

            form.save()

            return redirect(
                "finance:fee_structure_detail",
                pk=item.fee_structure.pk
            )

    else:

        form = FeeStructureItemForm(
            instance=item
        )

    return render(
        request,
        "finance/fee_structure_items/form.html",
        {
            "form": form,
            "structure": item.fee_structure,
        }
    )


@login_required
def fee_structure_item_delete(request, pk):

    item = get_object_or_404(
        FeeStructureItem,
        pk=pk
    )

    structure_id = item.fee_structure.pk

    if request.method == "POST":

        item.delete()

        return redirect(
            "finance:fee_structure_detail",
            pk=structure_id
        )

    return render(
        request,
        "finance/fee_structure_items/delete.html",
        {
            "item": item
        }
    )

@login_required
def invoice_list(request):

    invoices = (
        StudentInvoice.objects
        .select_related(
            "student",
            "enrollment",
        )
        .order_by(
            "-invoice_date"
        )
    )

    return render(
        request,
        "finance/invoices/list.html",
        {
            "invoices": invoices
        }
    )

@login_required
def invoice_detail(request, pk):

    invoice = get_object_or_404(
        StudentInvoice.objects.select_related(
            "student",
            "enrollment",
            "enrollment__academic_year",
            "enrollment__semester",
            "enrollment__programme_level",
        ),
        pk=pk
    )

    items = (
        invoice.items
        .select_related(
            "fee_category"
        )
    )

    payments = (
        invoice.payments
        .all()
        .order_by(
            "-payment_date",
            "-id"
        )
    )

    return render(
        request,
        "finance/invoices/detail.html",
        {
            "invoice": invoice,
            "items": items,
            "payments": payments,
        }
    )


@login_required
@transaction.atomic
def payment_create(request, invoice_id):

    invoice = get_object_or_404(
        StudentInvoice,
        pk=invoice_id,
    )

    if request.method == "POST":

        form = PaymentForm(
            request.POST,
            invoice=invoice,
        )

        if form.is_valid():

            payment = form.save(commit=False)

            payment.invoice = invoice
            payment.received_by = request.user

            try:

                payment.save()

            except ValidationError as e:

                messages.error(
                    request,
                    e.messages[0],
                )

                return render(
                    request,
                    "finance/payments/form.html",
                    {
                        "form": form,
                        "invoice": invoice,
                    },
                )

            # --------------------------------------------------
            # REFRESH INVOICE AFTER PAYMENT
            # --------------------------------------------------

            invoice.refresh_from_db()

            recalculate_invoice(invoice)

            # --------------------------------------------------
            # OVERPAYMENT / STUDENT CREDIT
            # --------------------------------------------------

            if (
                payment.posting_status == "POSTED"
                and not payment.is_reversed
                and invoice.balance_cached < Decimal("0.00")
            ):

                credit_amount = abs(
                    invoice.balance_cached
                )

                StudentCredit.objects.update_or_create(
                    source_payment=payment,
                    defaults={
                        "student": invoice.student,
                        "amount": credit_amount,
                    },
                )

            # --------------------------------------------------
            # RECEIPT
            # --------------------------------------------------

            Receipt.objects.get_or_create(
                payment=payment,
                defaults={
                    "created_by": request.user,
                },
            )

            # --------------------------------------------------
            # FINANCIAL CLEARANCE
            # --------------------------------------------------

            update_financial_clearance(
                invoice.enrollment,
                request.user,
            )

            messages.success(
                request,
                "Payment recorded successfully.",
            )

            return redirect(
                "finance:payment_detail",
                pk=payment.pk,
            )

    else:

        form = PaymentForm(
            invoice=invoice,
        )

    return render(
        request,
        "finance/payments/form.html",
        {
            "form": form,
            "invoice": invoice,
        },
    )

@login_required
def receipt_list(request):

    receipts = (
        Receipt.objects
        .select_related(
            "payment",
            "payment__invoice",
            "payment__invoice__student",
        )
    )

    return render(
        request,
        "finance/receipts/list.html",
        {
            "receipts": receipts,
        }
    )

@login_required
def receipt_detail(request, pk):

    receipt = get_object_or_404(
        Receipt.objects.select_related(
            "payment",
            "payment__invoice",
            "payment__invoice__student",
            "created_by",
        ),
        pk=pk
    )

    return render(
        request,
        "finance/receipts/detail.html",
        {
            "receipt": receipt,
        }
    )

@login_required
def payment_detail(request, pk):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "invoice",
            "invoice__student",
            "received_by",
        ),
        pk=pk
    )

    return render(
        request,
        "finance/payments/detail.html",
        {
            "payment": payment,
        }
    )

@login_required
def reverse_payment(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk
    )

    if payment.is_reversed:

        messages.warning(
            request,
            "This payment has already been reversed."
        )

        return redirect(
            "finance:payment_detail",
            pk=payment.pk
        )

    if request.method == "POST":

        form = ReversePaymentForm(request.POST)

        if form.is_valid():

            payment.is_reversed = True

            payment.posting_status = "REVERSED"

            payment.reversed_by = request.user

            payment.reversal_reason = form.cleaned_data[
                "reversal_reason"
            ]

            payment.save()

            # Reverse any credit created from this payment
            StudentCredit.objects.filter(
                source_payment=payment
            ).update(
                used_amount=0
            )

            # Recalculate financial clearance
            update_financial_clearance(
                payment.invoice.enrollment,
                request.user,
            )

            messages.success(
                request,
                "Payment reversed successfully."
            )

            return redirect(
                "finance:payment_detail",
                pk=payment.pk
            )

    else:

        form = ReversePaymentForm()

    return render(
        request,
        "finance/payments/reverse.html",
        {
            "payment": payment,
            "form": form,
        }
    )

@login_required
def payment_list(request):

    payments = (
        Payment.objects
        .select_related(
            "invoice",
            "invoice__student",
        )
    )

    return render(
        request,
        "finance/payments/list.html",
        {
            "payments": payments,
        }
    )


@login_required
def finance_settings(request):

    settings_obj, created = (
        FinanceSetting.objects.get_or_create(
            defaults={
                "minimum_registration_percentage": 30,
                "minimum_exam_percentage": 50,
                "minimum_result_slip_percentage": 70,
                "minimum_transcript_percentage": 100,
                "minimum_graduation_percentage": 100,
            }
        )
    )

    if request.method == "POST":

        form = FinanceSettingForm(
            request.POST,
            instance=settings_obj,
        )

        if form.is_valid():

            settings_obj = form.save()

            # ----------------------------------------
            # Recalculate ALL student financial
            # clearances using the new settings
            # ----------------------------------------

            enrollments = (
                SemesterEnrollment.objects.select_related(
                    "student",
                )
            )

            for enrollment in enrollments:

                update_financial_clearance(
                    enrollment,
                    request.user,
                )

            messages.success(
                request,
                "Finance settings updated successfully. "
                "All financial clearances have been recalculated.",
            )

            return redirect(
                "finance:settings",
            )

    else:

        form = FinanceSettingForm(
            instance=settings_obj,
        )

    return render(
        request,
        "finance/settings.html",
        {
            "form": form,
        },
    )

@login_required
def fee_statement_list(request):

    students = Student.objects.all()

    records = []

    for student in students:

        invoices = StudentInvoice.objects.filter(
            student=student
        )

        total_invoiced = sum(
            invoice.total_amount
            for invoice in invoices
        )

        total_paid = sum(
            invoice.amount_paid
            for invoice in invoices
        )

        balance = (
            total_invoiced
            - total_paid
        )

        records.append({
            "student": student,
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "balance": balance,
        })

    return render(
        request,
        "finance/statements/list.html",
        {
            "records": records,
        }
    )


@login_required
def fee_statement_detail(request, student_id):

    student = get_object_or_404(
        Student,
        pk=student_id
    )

    invoices = (
        StudentInvoice.objects
        .filter(student=student)
        .prefetch_related("payments")
        .order_by("invoice_date")
    )

    transactions = []

    total_invoiced = 0
    total_paid = 0

    for invoice in invoices:

        transactions.append({
            "date": invoice.invoice_date,
            "description": f"Invoice {invoice.invoice_number}",
            "status": "POSTED",
            "debit": invoice.total_amount,
            "credit": 0,
            "is_reversed": False,
        })

        total_invoiced += invoice.total_amount

        for payment in invoice.payments.all().order_by(
            "payment_date",
            "id",
        ):

            transactions.append({
                "date": payment.payment_date,
                "description": f"Payment {payment.payment_number}",
                "status": payment.posting_status,
                "debit": 0,
                "credit": payment.amount,
                "is_reversed": payment.is_reversed,
            })

            # Only posted payments count toward totals
            if not payment.is_reversed:
                total_paid += payment.amount

    transactions = sorted(
        transactions,
        key=lambda x: (x["date"], x["description"])
    )

    balance = total_invoiced - total_paid

    return render(
        request,
        "finance/statements/detail.html",
        {
            "student": student,
            "transactions": transactions,
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "balance": balance,
        }
    )


@login_required
def financial_clearance_list(request):

    settings = FinanceSetting.objects.first()

    invoices = (
        StudentInvoice.objects
        .select_related(
            "student",
            "enrollment"
        )
        .order_by(
            "student__admission_no"
        )
    )

    clearances = []

    for invoice in invoices:

        percentage = invoice.payment_percentage

        clearances.append({

            "invoice": invoice,

            "registration":
                percentage >= settings.minimum_registration_percentage,

            "exam":
                percentage >= settings.minimum_exam_percentage,

            "results":
                percentage >= settings.minimum_result_slip_percentage,

            "transcript":
                percentage >= settings.minimum_transcript_percentage,

            "graduation":
                percentage >= settings.minimum_graduation_percentage,

            "percentage": percentage,
        })

    return render(
        request,
        "finance/clearance/list.html",
        {
            "clearances": clearances,
        }
    )
