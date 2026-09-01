from decimal import Decimal
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from finance.services import update_financial_clearance
from students.models import SemesterEnrollment
from students.models import AcademicYear, Semester

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
    PaymentReversalForm,
)


# ==========================================================
# ACCESS CONTROL HELPERS
# ==========================================================

def get_logged_in_student(request):
    """
    Return the Student record belonging to the logged-in user.

    Returns None if the user is not linked to a Student record.
    """

    return (
        Student.objects
        .filter(user=request.user)
        .first()
    )


def is_finance_staff(request):
    """
    Determine whether the current user has Finance
    administrative access.

    Finance access is permission-based.
    """

    return (
        request.user.has_perm("finance.view_studentinvoice")
        or request.user.has_perm("finance.view_payment")
        or request.user.has_perm("finance.view_financialclearance")
        or request.user.has_perm("finance.view_feecategory")
        or request.user.has_perm("finance.view_feestructure")
        or request.user.has_perm("finance.view_financesetting")
    )


# ==========================================================
# FINANCE DASHBOARD
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.view_studentinvoice",
    raise_exception=True,
)
def finance_dashboard(request):

    today = timezone.localdate()

    # ======================================================
    # ACTIVE ACADEMIC YEAR
    # ======================================================

    active_academic_year = (
        AcademicYear.objects
        .filter(is_active=True)
        .first()
    )

    # ======================================================
    # ACTIVE SEMESTER
    # ======================================================

    active_semester = None

    if active_academic_year:

        active_semester = (
            Semester.objects
            .filter(
                academic_year=active_academic_year,
                is_active=True,
            )
            .first()
        )

    # ======================================================
    # VALID PAYMENTS
    #
    # Only POSTED and non-reversed payments count.
    # ======================================================

    payments = (
        Payment.objects
        .filter(
            posting_status="POSTED",
            is_reversed=False,
        )
    )

    semester_payments = payments

    if active_academic_year:

        semester_payments = semester_payments.filter(
            invoice__enrollment__academic_year=active_academic_year
        )

    if active_semester:

        semester_payments = semester_payments.filter(
            invoice__enrollment__semester=active_semester
        )

    # ======================================================
    # CURRENT PERIOD INVOICES
    # ======================================================

    invoices = StudentInvoice.objects.all()

    if active_academic_year:

        invoices = invoices.filter(
            enrollment__academic_year=active_academic_year
        )

    if active_semester:

        invoices = invoices.filter(
            enrollment__semester=active_semester
        )

    posted_invoices = invoices.filter(
        status="POSTED"
    )

    # ======================================================
    # COLLECTIONS
    # ======================================================

    total_collected = (
        semester_payments.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    today_collections = (
        semester_payments
        .filter(
            payment_date=today
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    week_start = (
        today -
        timedelta(days=today.weekday())
    )

    week_collections = (
        semester_payments
        .filter(
            payment_date__gte=week_start,
            payment_date__lte=today,
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    month_start = today.replace(day=1)

    month_collections = (
        semester_payments
        .filter(
            payment_date__gte=month_start,
            payment_date__lte=today,
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # ======================================================
    # GROSS INVOICED
    # ======================================================

    expected_revenue = (
        posted_invoices
        .aggregate(
            total=Sum("invoice_total")
        )["total"]
        or Decimal("0.00")
    )

    # ======================================================
    # CREDIT APPLIED
    #
    # IMPORTANT:
    # Read directly from StudentInvoice.credit_applied.
    #
    # This is the amount of previous/student credit that
    # has actually been applied against current invoices.
    # ======================================================

    credit_used_this_semester = (
        posted_invoices
        .aggregate(
            total=Sum("credit_applied")
        )["total"]
        or Decimal("0.00")
    )

    # ======================================================
    # ALIASES
    #
    # Provide all names the dashboard/template may use.
    # ======================================================

    previous_credit_applied = credit_used_this_semester
    credits_applied = credit_used_this_semester

    # ======================================================
    # OUTSTANDING BALANCE
    #
    # USE balance_cached FROM THE DATABASE.
    #
    # Do NOT calculate:
    #
    # invoice_total - amount_paid
    #
    # because credit may have been applied.
    # ======================================================

    outstanding_balance = (
        posted_invoices
        .filter(
            balance_cached__gt=Decimal("0.00")
        )
        .aggregate(
            total=Sum("balance_cached")
        )["total"]
        or Decimal("0.00")
    )

    # ======================================================
    # PENDING INVOICES
    # ======================================================

    pending_invoices = (
        posted_invoices
        .filter(
            balance_cached__gt=Decimal("0.00")
        )
        .count()
    )

    # ======================================================
    # RECEIPTS
    # ======================================================

    receipts_issued = semester_payments.count()

    # ======================================================
    # REVERSED PAYMENTS
    # ======================================================

    reversed_payments = (
        Payment.objects
        .filter(
            invoice__in=invoices,
            is_reversed=True,
        )
        .count()
    )

    # ======================================================
    # PAYMENT METHODS
    # ======================================================

    mpesa_total = (
        semester_payments
        .filter(payment_method="MPESA")
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    bank_total = (
        semester_payments
        .filter(payment_method="BANK")
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    cash_total = (
        semester_payments
        .filter(payment_method="CASH")
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    # ======================================================
    # PAYMENT SHARES
    # ======================================================

    if total_collected > 0:

        mpesa_share = round(
            (mpesa_total / total_collected) * 100,
            2,
        )

        bank_share = round(
            (bank_total / total_collected) * 100,
            2,
        )

        cash_share = round(
            (cash_total / total_collected) * 100,
            2,
        )

    else:

        mpesa_share = Decimal("0.00")
        bank_share = Decimal("0.00")
        cash_share = Decimal("0.00")

    other_share = max(
        Decimal("0.00"),
        Decimal("100.00")
        - Decimal(str(mpesa_share))
        - Decimal(str(bank_share))
        - Decimal(str(cash_share)),
    )

    # ======================================================
    # SETTLED VALUE
    #
    # Cash received for current invoices PLUS previous
    # credit applied to those invoices.
    # ======================================================

    settled_value = (
        total_collected
        + credit_used_this_semester
    )

    # ======================================================
    # COLLECTION RATE
    # ======================================================

    if expected_revenue > 0:

        collection_rate = round(
            (
                settled_value
                / expected_revenue
            ) * 100,
            2,
        )

    else:

        collection_rate = Decimal("0.00")

    collection_rate_display = min(
        float(collection_rate),
        100,
    )

    # ======================================================
    # BILLING SUMMARY
    # ======================================================

    total_invoiced_students = (
        posted_invoices
        .values("student_id")
        .distinct()
        .count()
    )

    fully_cleared = (
        posted_invoices
        .filter(
            balance_cached__lte=Decimal("0.00")
        )
        .values("student_id")
        .distinct()
        .count()
    )

    partially_paid = (
        posted_invoices
        .filter(
            balance_cached__gt=Decimal("0.00"),
            amount_paid_cached__gt=Decimal("0.00"),
        )
        .values("student_id")
        .distinct()
        .count()
    )

    not_paid = (
        posted_invoices
        .filter(
            amount_paid_cached__lte=Decimal("0.00"),
            credit_applied__lte=Decimal("0.00"),
            balance_cached__gt=Decimal("0.00"),
        )
        .values("student_id")
        .distinct()
        .count()
    )

    # ======================================================
    # PROJECTED CASH FLOW
    # ======================================================

    projected_cash_flow = outstanding_balance

    # ======================================================
    # BANK COLLECTIONS
    # ======================================================

    bank_reconciled = bank_total

    # ======================================================
    # REVENUE TREND
    # ======================================================

    revenue_labels = []
    revenue_values = []

    for month in range(1, 13):

        monthly_total = (
            semester_payments
            .filter(
                payment_date__year=today.year,
                payment_date__month=month,
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        revenue_labels.append(
            timezone.datetime(
                today.year,
                month,
                1,
            ).strftime("%b")
        )

        revenue_values.append(
            float(monthly_total)
        )

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {

        # ==================================================
        # ACADEMIC PERIOD
        # ==================================================

        "active_academic_year": active_academic_year,
        "active_semester": active_semester,

        # ==================================================
        # COLLECTIONS
        # ==================================================

        "total_collected": total_collected,
        "total_fees_collected": total_collected,

        "today_collections": today_collections,
        "todays_collections": today_collections,

        "week_collections": week_collections,
        "weekly_collections": week_collections,

        "month_collections": month_collections,
        "monthly_collections": month_collections,

        # ==================================================
        # INVOICING
        # ==================================================

        "expected_revenue": expected_revenue,
        "gross_invoiced": expected_revenue,

        # ==================================================
        # CREDIT
        #
        # All three aliases intentionally point to the same
        # database value.
        # ==================================================

        "credit_used_this_semester": credit_used_this_semester,
        "credits_applied": credits_applied,
        "previous_credit_applied": previous_credit_applied,

        # ==================================================
        # SETTLEMENT
        # ==================================================

        "settled_value": settled_value,
        "collection_rate": collection_rate,
        "collection_rate_display": collection_rate_display,

        # ==================================================
        # BALANCE
        # ==================================================

        "outstanding_balance": outstanding_balance,
        "outstanding_balances": outstanding_balance,

        "pending_invoices": pending_invoices,

        # ==================================================
        # BILLING
        # ==================================================

        "fully_cleared": fully_cleared,

        "partially_paid": partially_paid,
        "partially_cleared": partially_paid,

        "not_paid": not_paid,
        "not_cleared": not_paid,

        "total_invoiced_students": total_invoiced_students,

        # ==================================================
        # RECEIPTS
        # ==================================================

        "receipts_issued": receipts_issued,
        "reversed_payments": reversed_payments,

        # ==================================================
        # PAYMENT METHODS
        # ==================================================

        "mpesa_total": mpesa_total,
        "bank_total": bank_total,
        "cash_total": cash_total,

        "mpesa_share": mpesa_share,
        "bank_share": bank_share,
        "cash_share": cash_share,
        "other_share": other_share,

        # ==================================================
        # OTHER
        # ==================================================

        "projected_cash_flow": projected_cash_flow,
        "bank_reconciled": bank_reconciled,

        # ==================================================
        # CHARTS
        # ==================================================

        "revenue_labels": revenue_labels,
        "revenue_values": revenue_values,

        "category_labels": [
            "M-Pesa",
            "Bank",
            "Cash",
        ],

        "category_values": [
            float(mpesa_total),
            float(bank_total),
            float(cash_total),
        ],
    }

    return render(
        request,
        "students/dashboards/finance_home.html",
        context,
    )


# ==========================================================
# FEE CATEGORIES
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.view_feecategory",
    raise_exception=True,
)
def fee_category_list(request):

    categories = (
        FeeCategory.objects
        .all()
        .order_by("name")
    )

    return render(
        request,
        "finance/fee_categories/list.html",
        {
            "categories": categories,
        },
    )


@login_required
@permission_required(
    "finance.add_feecategory",
    raise_exception=True,
)
def fee_category_create(request):

    if request.method == "POST":

        form = FeeCategoryForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee category created successfully.",
            )

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm()

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form,
        },
    )


@login_required
@permission_required(
    "finance.change_feecategory",
    raise_exception=True,
)
def fee_category_update(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk,
    )

    if request.method == "POST":

        form = FeeCategoryForm(
            request.POST,
            instance=category,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee category updated successfully.",
            )

            return redirect(
                "finance:fee_category_list"
            )

    else:

        form = FeeCategoryForm(
            instance=category,
        )

    return render(
        request,
        "finance/fee_categories/form.html",
        {
            "form": form,
            "category": category,
        },
    )


@login_required
@permission_required(
    "finance.delete_feecategory",
    raise_exception=True,
)
def fee_category_delete(request, pk):

    category = get_object_or_404(
        FeeCategory,
        pk=pk,
    )

    if request.method == "POST":

        category.delete()

        messages.success(
            request,
            "Fee category deleted successfully.",
        )

        return redirect(
            "finance:fee_category_list"
        )

    return render(
        request,
        "finance/fee_categories/delete.html",
        {
            "category": category,
        },
    )


# ==========================================================
# FEE STRUCTURES
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.view_feestructure",
    raise_exception=True,
)
def fee_structure_list(request):

    fee_structures = (
        FeeStructure.objects
        .select_related(
            "programme_level",
            "academic_year",
            "semester",
        )
        .order_by(
            "-academic_year",
            "semester",
        )
    )

    return render(
        request,
        "finance/fee_structures/list.html",
        {
            "fee_structures": fee_structures,
        },
    )


@login_required
@permission_required(
    "finance.add_feestructure",
    raise_exception=True,
)
def fee_structure_create(request):

    if request.method == "POST":

        form = FeeStructureForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee structure created successfully.",
            )

            return redirect(
                "finance:fee_structure_list"
            )

    else:

        form = FeeStructureForm()

    return render(
        request,
        "finance/fee_structures/form.html",
        {
            "form": form,
        },
    )


@login_required
@permission_required(
    "finance.view_feestructure",
    raise_exception=True,
)
def fee_structure_detail(request, pk):

    structure = get_object_or_404(
        FeeStructure,
        pk=pk,
    )

    items = (
        structure.items
        .select_related(
            "fee_category",
        )
        .order_by(
            "fee_category__name"
        )
    )

    return render(
        request,
        "finance/fee_structures/detail.html",
        {
            "structure": structure,
            "items": items,
        },
    )


@login_required
@permission_required(
    "finance.add_feestructureitem",
    raise_exception=True,
)
def fee_structure_item_create(
    request,
    structure_id,
):

    structure = get_object_or_404(
        FeeStructure,
        pk=structure_id,
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

            messages.success(
                request,
                "Fee structure item added successfully.",
            )

            return redirect(
                "finance:fee_structure_detail",
                pk=structure.id,
            )

    else:

        form = FeeStructureItemForm()

    return render(
        request,
        "finance/fee_structure_items/form.html",
        {
            "form": form,
            "structure": structure,
        },
    )


@login_required
@permission_required(
    "finance.change_feestructureitem",
    raise_exception=True,
)
def fee_structure_item_update(request, pk):

    item = get_object_or_404(
        FeeStructureItem,
        pk=pk,
    )

    if request.method == "POST":

        form = FeeStructureItemForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Fee structure item updated successfully.",
            )

            return redirect(
                "finance:fee_structure_detail",
                pk=item.fee_structure.pk,
            )

    else:

        form = FeeStructureItemForm(
            instance=item,
        )

    return render(
        request,
        "finance/fee_structure_items/form.html",
        {
            "form": form,
            "structure": item.fee_structure,
        },
    )


@login_required
@permission_required(
    "finance.delete_feestructureitem",
    raise_exception=True,
)
def fee_structure_item_delete(request, pk):

    item = get_object_or_404(
        FeeStructureItem,
        pk=pk,
    )

    structure_id = item.fee_structure.pk

    if request.method == "POST":

        item.delete()

        messages.success(
            request,
            "Fee structure item deleted successfully.",
        )

        return redirect(
            "finance:fee_structure_detail",
            pk=structure_id,
        )

    return render(
        request,
        "finance/fee_structure_items/delete.html",
        {
            "item": item,
        },
    )


# ==========================================================
# INVOICES
#
# Finance staff can see ALL invoices.
# Students can see ONLY their own invoices.
# ==========================================================

@login_required
def invoice_list(request):

    if is_finance_staff(request):

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

    else:

        student = get_logged_in_student(request)

        if not student:

            messages.error(
                request,
                "Your account is not linked to a student record.",
            )

            return redirect("home")

        invoices = (
            StudentInvoice.objects
            .filter(
                student=student,
            )
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
            "invoices": invoices,
        },
    )


@login_required
def invoice_detail(request, pk):

    invoice = get_object_or_404(
        StudentInvoice.objects
        .select_related(
            "student",
            "enrollment",
            "enrollment__academic_year",
            "enrollment__semester",
            "enrollment__programme_level",
        ),
        pk=pk,
    )

    if not is_finance_staff(request):

        student = get_logged_in_student(request)

        if (
            not student
            or invoice.student_id != student.id
        ):

            messages.error(
                request,
                "You are not authorized to view this invoice.",
            )

            return redirect("home")

    items = (
        invoice.items
        .select_related(
            "fee_category",
        )
    )

    payments = (
        invoice.payments
        .all()
        .order_by(
            "-payment_date",
            "-id",
        )
    )

    return render(
        request,
        "finance/invoices/detail.html",
        {
            "invoice": invoice,
            "items": items,
            "payments": payments,
        },
    )


# ==========================================================
# PAYMENT CREATION
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.add_payment",
    raise_exception=True,
)
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

            payment = form.save(
                commit=False
            )

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

            # ==================================================
            # CREATE STUDENT CREDIT IF OVERPAYMENT EXISTS
            # ==================================================

            if invoice.balance < 0:

                StudentCredit.objects.get_or_create(
                    source_payment=payment,
                    defaults={
                        "student": invoice.student,
                        "amount": abs(
                            invoice.balance
                        ),
                    },
                )

            # ==================================================
            # GENERATE RECEIPT
            # ==================================================

            Receipt.objects.get_or_create(
                payment=payment,
                defaults={
                    "created_by": request.user,
                },
            )

            # ==================================================
            # UPDATE FINANCIAL CLEARANCE
            # ==================================================

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


# ==========================================================
# RECEIPTS
# ==========================================================

@login_required
def receipt_list(request):

    if is_finance_staff(request):

        receipts = (
            Receipt.objects
            .select_related(
                "payment",
                "payment__invoice",
                "payment__invoice__student",
            )
            .order_by(
                "-payment__payment_date",
                "-id",
            )
        )

    else:

        student = get_logged_in_student(request)

        if not student:

            messages.error(
                request,
                "Your account is not linked to a student record.",
            )

            return redirect("home")

        receipts = (
            Receipt.objects
            .filter(
                payment__invoice__student=student,
            )
            .select_related(
                "payment",
                "payment__invoice",
                "payment__invoice__student",
            )
            .order_by(
                "-payment__payment_date",
                "-id",
            )
        )

    return render(
        request,
        "finance/receipts/list.html",
        {
            "receipts": receipts,
        },
    )


@login_required
def receipt_detail(request, pk):

    receipt = get_object_or_404(
        Receipt.objects
        .select_related(
            "payment",
            "payment__invoice",
            "payment__invoice__student",
            "created_by",
        ),
        pk=pk,
    )

    if not is_finance_staff(request):

        student = get_logged_in_student(request)

        if (
            not student
            or receipt.payment.invoice.student_id != student.id
        ):

            messages.error(
                request,
                "You are not authorized to view this receipt.",
            )

            return redirect("home")

    return render(
        request,
        "finance/receipts/detail.html",
        {
            "receipt": receipt,
        },
    )


# ==========================================================
# PAYMENT DETAILS
# ==========================================================

@login_required
def payment_detail(request, pk):

    payment = get_object_or_404(
        Payment.objects
        .select_related(
            "invoice",
            "invoice__student",
            "received_by",
        ),
        pk=pk,
    )

    if not is_finance_staff(request):

        student = get_logged_in_student(request)

        if (
            not student
            or payment.invoice.student_id != student.id
        ):

            messages.error(
                request,
                "You are not authorized to view this payment.",
            )

            return redirect("home")

    return render(
        request,
        "finance/payments/detail.html",
        {
            "payment": payment,
        },
    )


# ==========================================================
# PAYMENT REVERSAL
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.change_payment",
    raise_exception=True,
)
def reverse_payment(request, pk):

    payment = get_object_or_404(
        Payment,
        pk=pk,
    )

    if payment.is_reversed:

        messages.warning(
            request,
            "This payment has already been reversed.",
        )

        return redirect(
            "finance:payment_detail",
            pk=payment.pk,
        )

    if request.method == "POST":

        form = ReversePaymentForm(
            request.POST
        )

        if form.is_valid():

            payment.is_reversed = True
            payment.posting_status = "REVERSED"
            payment.reversed_by = request.user
            payment.reversal_reason = (
                form.cleaned_data["reversal_reason"]
            )

            payment.save()

            # ==================================================
            # REVERSE CREDIT CREATED FROM PAYMENT
            # ==================================================

            StudentCredit.objects.filter(
                source_payment=payment
            ).update(
                used_amount=0
            )

            # ==================================================
            # RECALCULATE FINANCIAL CLEARANCE
            # ==================================================

            update_financial_clearance(
                payment.invoice.enrollment,
                request.user,
            )

            messages.success(
                request,
                "Payment reversed successfully.",
            )

            return redirect(
                "finance:payment_detail",
                pk=payment.pk,
            )

    else:

        form = ReversePaymentForm()

    return render(
        request,
        "finance/payments/reverse.html",
        {
            "payment": payment,
            "form": form,
        },
    )


# ==========================================================
# PAYMENT LIST
# ==========================================================

@login_required
def payment_list(request):

    if is_finance_staff(request):

        payments = (
            Payment.objects
            .select_related(
                "invoice",
                "invoice__student",
            )
            .order_by(
                "-payment_date",
                "-id",
            )
        )

    else:

        student = get_logged_in_student(request)

        if not student:

            messages.error(
                request,
                "Your account is not linked to a student record.",
            )

            return redirect("home")

        payments = (
            Payment.objects
            .filter(
                invoice__student=student,
            )
            .select_related(
                "invoice",
                "invoice__student",
            )
            .order_by(
                "-payment_date",
                "-id",
            )
        )

    return render(
        request,
        "finance/payments/list.html",
        {
            "payments": payments,
        },
    )


# ==========================================================
# FINANCE SETTINGS
# STAFF ONLY
# ==========================================================

@login_required
@permission_required(
    "finance.view_financesetting",
    raise_exception=True,
)
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

        if not request.user.has_perm(
            "finance.change_financesetting"
        ):

            messages.error(
                request,
                "You are not authorized to modify Finance settings.",
            )

            return redirect(
                "finance:settings"
            )

        form = FinanceSettingForm(
            request.POST,
            instance=settings_obj,
        )

        if form.is_valid():

            settings_obj = form.save()

            # ==================================================
            # RECALCULATE ALL FINANCIAL CLEARANCES
            # ==================================================

            enrollments = (
                SemesterEnrollment.objects
                .select_related(
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
                "finance:settings"
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


# ==========================================================
# FEE STATEMENT LIST
#
# Finance staff see all students.
# Students see ONLY their own statement.
# ==========================================================

@login_required
def fee_statement_list(request):

    if is_finance_staff(request):

        students = (
            Student.objects
            .all()
            .order_by("admission_no")
        )

    else:

        student = get_logged_in_student(request)

        if not student:

            messages.error(
                request,
                "Your account is not linked to a student record.",
            )

            return redirect("home")

        students = Student.objects.filter(
            pk=student.pk
        )

    records = []

    for student in students:

        invoices = (
            StudentInvoice.objects
            .filter(
                student=student
            )
        )

        total_invoiced = (
            invoices.aggregate(
                total=Sum("invoice_total")
            )["total"]
            or Decimal("0.00")
        )

        total_paid = (
            invoices.aggregate(
                total=Sum("amount_paid_cached")
            )["total"]
            or Decimal("0.00")
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
        },
    )


# ==========================================================
# FEE STATEMENT DETAIL
#
# Finance staff may view any student.
# Students may view only themselves.
# ==========================================================

@login_required
def fee_statement_detail(request, student_id):

    student = get_object_or_404(
        Student,
        pk=student_id,
    )

    if not is_finance_staff(request):

        logged_in_student = get_logged_in_student(
            request
        )

        if (
            not logged_in_student
            or logged_in_student.id != student.id
        ):

            messages.error(
                request,
                "You are not authorized to view this student's "
                "financial statement.",
            )

            return redirect("home")

    invoices = (
        StudentInvoice.objects
        .filter(
            student=student,
            status="POSTED",
        )
        .prefetch_related(
            "payments"
        )
        .order_by(
            "invoice_date"
        )
    )

    transactions = []

    total_invoiced = Decimal("0.00")
    total_paid = Decimal("0.00")
    previous_credit_applied = Decimal("0.00")

    for invoice in invoices:

        # ==================================================
        # INVOICE
        # ==================================================

        transactions.append({
            "date": invoice.invoice_date,
            "description": (
                f"Invoice {invoice.invoice_number}"
            ),
            "status": "POSTED",
            "debit": invoice.invoice_total,
            "credit": Decimal("0.00"),
            "is_reversed": False,
        })

        total_invoiced += (
            invoice.invoice_total
            or Decimal("0.00")
        )

        # ==================================================
        # PREVIOUS CREDIT APPLIED
        #
        # This is stored on the invoice itself.
        # ==================================================

        invoice_credit = (
            invoice.credit_applied
            or Decimal("0.00")
        )

        previous_credit_applied += invoice_credit

        # ==================================================
        # SHOW CREDIT AS A CREDIT TRANSACTION
        #
        # This makes the KSh 1,000 visible in the statement.
        # ==================================================

        if invoice_credit > Decimal("0.00"):

            transactions.append({
                "date": invoice.invoice_date,
                "description": (
                    f"Previous Credit Applied "
                    f"to {invoice.invoice_number}"
                ),
                "status": "CREDIT_APPLIED",
                "debit": Decimal("0.00"),
                "credit": invoice_credit,
                "is_reversed": False,
            })

        # ==================================================
        # PAYMENTS
        # ==================================================

        for payment in invoice.payments.all().order_by(
            "payment_date",
            "id",
        ):

            transactions.append({
                "date": payment.payment_date,
                "description": (
                    f"Payment {payment.payment_number}"
                ),
                "status": payment.posting_status,
                "debit": Decimal("0.00"),
                "credit": payment.amount,
                "is_reversed": payment.is_reversed,
            })

            if (
                payment.posting_status == "POSTED"
                and not payment.is_reversed
            ):

                total_paid += (
                    payment.amount
                    or Decimal("0.00")
                )

    # ======================================================
    # TOTAL SETTLED
    # ======================================================

    total_settled = (
        total_paid
        + previous_credit_applied
    )

    # ======================================================
    # ACTUAL BALANCE
    #
    # Use the database cached balance instead of manually
    # calculating invoice_total - payments.
    # ======================================================

    balance = (
        invoices.aggregate(
            total=Sum("balance_cached")
        )["total"]
        or Decimal("0.00")
    )

    if balance < Decimal("0.00"):
        balance = Decimal("0.00")

    # ======================================================
    # SORT TRANSACTIONS
    # ======================================================

    transactions = sorted(
        transactions,
        key=lambda x: (
            x["date"],
            x["description"],
        )
    )

    # ======================================================
    # CONTEXT
    # ======================================================

    return render(
        request,
        "finance/statements/detail.html",
        {
            "student": student,

            "transactions": transactions,

            "total_invoiced": total_invoiced,

            "total_paid": total_paid,

            "previous_credit_applied": (
                previous_credit_applied
            ),

            "credit_applied": (
                previous_credit_applied
            ),

            "total_settled": total_settled,

            "balance": balance,
        },
    )



# ==========================================================
# FINANCIAL CLEARANCE
#
# Finance staff see all.
# Students may view ONLY their own financial clearance.
# ==========================================================

@login_required
def financial_clearance_list(request):

    finance_settings_obj = (
        FinanceSetting.objects
        .first()
    )

    if not finance_settings_obj:

        messages.error(
            request,
            "Finance settings have not been configured.",
        )

        return redirect("home")

    if is_finance_staff(request):

        invoices = (
            StudentInvoice.objects
            .select_related(
                "student",
                "enrollment",
            )
            .order_by(
                "student__admission_no"
            )
        )

    else:

        student = get_logged_in_student(request)

        if not student:

            messages.error(
                request,
                "Your account is not linked to a student record.",
            )

            return redirect("home")

        invoices = (
            StudentInvoice.objects
            .filter(
                student=student,
            )
            .select_related(
                "student",
                "enrollment",
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

            "registration": (
                percentage
                >= finance_settings_obj
                .minimum_registration_percentage
            ),

            "exam": (
                percentage
                >= finance_settings_obj
                .minimum_exam_percentage
            ),

            "results": (
                percentage
                >= finance_settings_obj
                .minimum_result_slip_percentage
            ),

            "transcript": (
                percentage
                >= finance_settings_obj
                .minimum_transcript_percentage
            ),

            "graduation": (
                percentage
                >= finance_settings_obj
                .minimum_graduation_percentage
            ),

            "percentage": percentage,
        })

    return render(
        request,
        "finance/clearance/list.html",
        {
            "clearances": clearances,
        },
    )