from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from finance.models import Payment, StudentInvoice
from students.models import (
    Department,
    Programme,
    Semester,
    SemesterEnrollment,
)


ZERO = Decimal("0.00")
HUNDRED = Decimal("100.00")


# ============================================================
# NUMERIC HELPERS
# ============================================================

def to_decimal(value):
    """
    Safely normalize database/Python numeric values to Decimal.
    """

    if value is None:
        return ZERO

    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ZERO


def money(value):
    return to_decimal(value).quantize(
        Decimal("0.01")
    )


def percentage(value):
    return to_decimal(value).quantize(
        Decimal("0.1")
    )


# ============================================================
# PAYMENT STATUS
# ============================================================

def get_posted_payment_status():
    """
    Resolve the POSTED value from the Payment model.
    """

    choices = getattr(
        Payment,
        "POSTING_STATUS_CHOICES",
        [],
    )

    for value, label in choices:

        if str(label).strip().upper() == "POSTED":
            return value

    return getattr(
        Payment,
        "POSTED",
        "POSTED",
    )


# ============================================================
# USER-SCOPED ENROLLMENTS
# ============================================================

def get_financial_transactions_enrollments(user):

    enrollments = (
        SemesterEnrollment.objects
        .select_related(
            "student",
            "programme",
            "programme__course",
            "programme__course__department",
            "academic_year",
            "semester",
        )
    )

    if user.groups.filter(name="HOD").exists():

        enrollments = enrollments.filter(
            programme__course__department__hod=user
        )

    return enrollments


# ============================================================
# USER-SCOPED INVOICES
# ============================================================

def get_financial_transactions_invoices(user):

    enrollment_ids = (
        get_financial_transactions_enrollments(user)
        .values_list(
            "id",
            flat=True,
        )
    )

    return (
        StudentInvoice.objects
        .filter(
            enrollment_id__in=enrollment_ids,
        )
        .select_related(
            "student",
            "enrollment",
            "enrollment__academic_year",
            "enrollment__semester",
            "student__programme",
            "student__programme__course",
            "student__programme__course__department",
        )
    )


# ============================================================
# AVAILABLE SEMESTERS
# ============================================================

def get_all_semesters(user):

    semester_ids = (
        get_financial_transactions_enrollments(user)
        .exclude(
            semester_id__isnull=True,
        )
        .values_list(
            "semester_id",
            flat=True,
        )
        .distinct()
    )

    return (
        Semester.objects
        .filter(
            id__in=semester_ids,
        )
        .select_related(
            "academic_year",
        )
        .order_by(
            "start_date",
            "id",
        )
    )


# ============================================================
# CURRENT SEMESTER
# ============================================================

def get_current_semester(user):

    today = timezone.localdate()

    semesters = get_all_semesters(user)

    current = (
        semesters
        .filter(
            start_date__isnull=False,
            end_date__isnull=False,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by(
            "start_date",
            "id",
        )
        .first()
    )

    if current:
        return current

    return (
        semesters
        .exclude(
            start_date__isnull=True,
        )
        .order_by(
            "-start_date",
            "-id",
        )
        .first()
    )


# ============================================================
# PREVIOUS SEMESTER
# ============================================================

def get_previous_semester(
    user,
    current_semester,
):

    if current_semester is None:
        return None

    semesters = list(
        get_all_semesters(user)
    )

    if not semesters:
        return None

    current_index = None

    for index, semester in enumerate(semesters):

        if semester.id == current_semester.id:
            current_index = index
            break

    if current_index is not None:

        if current_index > 0:
            return semesters[current_index - 1]

        return None

    current_start_date = getattr(
        current_semester,
        "start_date",
        None,
    )

    if current_start_date is None:
        return None

    return (
        Semester.objects
        .filter(
            start_date__isnull=False,
            start_date__lt=current_start_date,
        )
        .select_related(
            "academic_year",
        )
        .order_by(
            "-start_date",
            "-id",
        )
        .first()
    )


# ============================================================
# FILTERS
# ============================================================

def apply_department_programme_filters(
    invoices,
    department_id=None,
    programme_id=None,
):

    if department_id:

        invoices = invoices.filter(
            student__programme__course__department_id=
            department_id
        )

    if programme_id:

        invoices = invoices.filter(
            student__programme_id=programme_id
        )

    return invoices


# ============================================================
# SEMESTER INVOICES
# ============================================================

def get_semester_invoices(
    user,
    semester,
    department_id=None,
    programme_id=None,
):

    if semester is None:
        return StudentInvoice.objects.none()

    invoices = get_financial_transactions_invoices(
        user
    )

    invoices = invoices.filter(
        enrollment__semester_id=semester.id,
    )

    invoices = apply_department_programme_filters(
        invoices,
        department_id=department_id,
        programme_id=programme_id,
    )

    return invoices


# ============================================================
# OUTSTANDING FEES REPORT
# ============================================================

def get_outstanding_fees_report(
    user,
    semester_id=None,
    department_id=None,
    programme_id=None,
    search="",
):

    # --------------------------------------------------------
    # SELECT SEMESTER
    # --------------------------------------------------------

    semesters = get_all_semesters(user)

    selected_semester = None

    if semester_id:

        try:

            selected_semester = semesters.filter(
                pk=int(semester_id)
            ).first()

        except (
            ValueError,
            TypeError,
        ):

            selected_semester = None

    if selected_semester is None:

        selected_semester = get_current_semester(
            user
        )

    # --------------------------------------------------------
    # BASE INVOICES
    # --------------------------------------------------------

    if selected_semester is None:

        return {
            "semester": None,
            "semester_id": None,
            "rows": [],
            "summary": {
                "student_count": 0,
                "invoice_count": 0,
                "gross_invoiced": ZERO,
                "cash_collections": ZERO,
                "credits_applied": ZERO,
                "outstanding": ZERO,
                "average_outstanding": ZERO,
            },
        }

    invoices = get_semester_invoices(
        user,
        selected_semester,
        department_id=department_id,
        programme_id=programme_id,
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        from django.db.models import Q

        invoices = invoices.filter(
            Q(
                student__first_name__icontains=search
            )
            |
            Q(
                student__middle_name__icontains=search
            )
            |
            Q(
                student__last_name__icontains=search
            )
            |
            Q(
                student__admission_number__icontains=search
            )
            |
            Q(
                student__registration_number__icontains=search
            )
            |
            Q(
                invoice_number__icontains=search
            )
        )

    # --------------------------------------------------------
    # ONLY POSITIVE OUTSTANDING BALANCES
    # --------------------------------------------------------

    invoices = invoices.filter(
        balance_cached__gt=ZERO
    )

    invoices = invoices.order_by(
        "-balance_cached",
        "student__last_name",
        "student__first_name",
    )

    # --------------------------------------------------------
    # BUILD STUDENT ROWS
    #
    # A student may have more than one invoice.
    # Group all invoices belonging to the same student.
    # --------------------------------------------------------

    student_data = {}

    posted_status = get_posted_payment_status()

    for invoice in invoices:

        student = invoice.student

        student_id = student.id

        if student_id not in student_data:

            programme = getattr(
                student,
                "programme",
                None,
            )

            course = (
                getattr(
                    programme,
                    "course",
                    None,
                )
                if programme
                else None
            )

            department = (
                getattr(
                    course,
                    "department",
                    None,
                )
                if course
                else None
            )

            student_data[student_id] = {
                "student_id": student_id,
                "student": student,
                "student_name": (
                    student.get_full_name()
                    if hasattr(
                        student,
                        "get_full_name",
                    )
                    else str(student)
                ),
                "admission_number": (
                    getattr(
                        student,
                        "admission_number",
                        None,
                    )
                    or getattr(
                        student,
                        "registration_number",
                        None,
                    )
                    or "-"
                ),
                "programme": (
                    programme.name
                    if programme
                    else "-"
                ),
                "programme_id": (
                    programme.id
                    if programme
                    else None
                ),
                "department": (
                    department.name
                    if department
                    else "-"
                ),
                "department_id": (
                    department.id
                    if department
                    else None
                ),
                "invoice_count": 0,
                "gross_invoiced": ZERO,
                "cash_collections": ZERO,
                "credits_applied": ZERO,
                "outstanding": ZERO,
            }

        row = student_data[student_id]

        row["invoice_count"] += 1

        row["gross_invoiced"] += money(
            invoice.invoice_total
        )

        row["credits_applied"] += money(
            invoice.credit_applied
        )

        row["outstanding"] += max(
            ZERO,
            money(invoice.balance_cached),
        )

        cash = (
            Payment.objects
            .filter(
                invoice=invoice,
                posting_status=posted_status,
                is_reversed=False,
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
        )

        row["cash_collections"] += money(
            cash
        )

    # --------------------------------------------------------
    # FINAL ROWS
    # --------------------------------------------------------

    rows = []

    for row in student_data.values():

        row["gross_invoiced"] = money(
            row["gross_invoiced"]
        )

        row["cash_collections"] = money(
            row["cash_collections"]
        )

        row["credits_applied"] = money(
            row["credits_applied"]
        )

        row["outstanding"] = money(
            row["outstanding"]
        )

        rows.append(row)

    rows.sort(
        key=lambda row: (
            -row["outstanding"],
            row["student_name"] or "",
        )
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    gross_invoiced = sum(
        (
            row["gross_invoiced"]
            for row in rows
        ),
        ZERO,
    )

    cash_collections = sum(
        (
            row["cash_collections"]
            for row in rows
        ),
        ZERO,
    )

    credits_applied = sum(
        (
            row["credits_applied"]
            for row in rows
        ),
        ZERO,
    )

    outstanding = sum(
        (
            row["outstanding"]
            for row in rows
        ),
        ZERO,
    )

    student_count = len(rows)

    invoice_count = sum(
        (
            row["invoice_count"]
            for row in rows
        ),
        0,
    )

    if student_count:

        average_outstanding = (
            outstanding
            / Decimal(student_count)
        )

    else:

        average_outstanding = ZERO

    summary = {
        "student_count": student_count,
        "invoice_count": invoice_count,
        "gross_invoiced": money(
            gross_invoiced
        ),
        "cash_collections": money(
            cash_collections
        ),
        "credits_applied": money(
            credits_applied
        ),
        "outstanding": money(
            outstanding
        ),
        "average_outstanding": money(
            average_outstanding
        ),
    }

    return {
        "semester": selected_semester,
        "semester_id": selected_semester.id,
        "rows": rows,
        "summary": summary,
    }


# ============================================================
# SEMESTER METRICS
# ============================================================

def calculate_semester_metrics(
    user,
    semester,
    department_id=None,
    programme_id=None,
):

    if semester is None:

        return {
            "semester": None,
            "invoice_count": 0,
            "student_count": 0,
            "gross_invoiced": ZERO,
            "cash_collections": ZERO,
            "credits_applied": ZERO,
            "outstanding": ZERO,
            "overpayment_credit": ZERO,
            "transaction_count": 0,
            "average_transaction": ZERO,
            "settlement_rate": ZERO,
            "cash_collection_rate": ZERO,
        }

    invoices = get_semester_invoices(
        user,
        semester,
        department_id=department_id,
        programme_id=programme_id,
    )

    summary = invoices.aggregate(
        gross=Sum("invoice_total"),
        balance=Sum("balance_cached"),
        credits=Sum("credit_applied"),
    )

    gross = money(
        summary["gross"]
    )

    raw_balance = money(
        summary["balance"]
    )

    credits = money(
        summary["credits"]
    )

    if raw_balance > ZERO:

        outstanding = raw_balance
        overpayment_credit = ZERO

    elif raw_balance < ZERO:

        outstanding = ZERO
        overpayment_credit = abs(
            raw_balance
        )

    else:

        outstanding = ZERO
        overpayment_credit = ZERO

    posted_status = (
        get_posted_payment_status()
    )

    payments = (
        Payment.objects
        .filter(
            invoice__in=invoices,
            posting_status=posted_status,
            is_reversed=False,
        )
    )

    cash = money(
        payments.aggregate(
            total=Sum("amount")
        )["total"]
    )

    transaction_count = payments.count()

    if transaction_count:

        average_transaction = (
            cash
            / Decimal(transaction_count)
        )

    else:

        average_transaction = ZERO

    student_count = (
        invoices
        .values("student_id")
        .distinct()
        .count()
    )

    invoice_count = invoices.count()

    if gross > ZERO:

        settlement = (
            (gross - outstanding)
            / gross
            * HUNDRED
        )

        settlement = max(
            ZERO,
            min(
                HUNDRED,
                settlement,
            ),
        )

        cash_rate = (
            cash
            / gross
            * HUNDRED
        )

    else:

        settlement = ZERO
        cash_rate = ZERO

    return {
        "semester": semester,
        "invoice_count": invoice_count,
        "student_count": student_count,
        "gross_invoiced": money(gross),
        "cash_collections": money(cash),
        "credits_applied": money(credits),
        "outstanding": money(outstanding),
        "overpayment_credit": money(
            overpayment_credit
        ),
        "transaction_count":
            transaction_count,
        "average_transaction":
            money(average_transaction),
        "settlement_rate":
            percentage(settlement),
        "cash_collection_rate":
            percentage(cash_rate),
    }


# ============================================================
# CHANGE CALCULATIONS
# ============================================================

def calculate_change(
    current,
    previous,
):

    current = to_decimal(current)
    previous = to_decimal(previous)

    amount_change = (
        current - previous
    )

    if previous == ZERO:

        if current == ZERO:
            percent_change = ZERO
        else:
            percent_change = None

    else:

        percent_change = (
            amount_change
            / abs(previous)
            * HUNDRED
        )

    return {
        "amount": money(
            amount_change
        ),
        "percent": (
            percentage(
                percent_change
            )
            if percent_change is not None
            else None
        ),
    }


def calculate_rate_change(
    current,
    previous,
):

    current = to_decimal(current)
    previous = to_decimal(previous)

    return percentage(
        current - previous
    )


# ============================================================
# COMPARISON
# ============================================================

def build_comparison(
    current,
    previous,
):

    if current is None:

        return {
            "available": False,
            "message":
                "No current semester is available.",
        }

    if previous is None:

        return {
            "available": False,
            "message":
                "No previous semester is available "
                "for comparison.",
        }

    return {
        "available": True,

        "gross_invoiced": calculate_change(
            current["gross_invoiced"],
            previous["gross_invoiced"],
        ),

        "cash_collections": calculate_change(
            current["cash_collections"],
            previous["cash_collections"],
        ),

        "credits_applied": calculate_change(
            current["credits_applied"],
            previous["credits_applied"],
        ),

        "outstanding": calculate_change(
            current["outstanding"],
            previous["outstanding"],
        ),

        "overpayment_credit": calculate_change(
            current["overpayment_credit"],
            previous["overpayment_credit"],
        ),

        "settlement_rate": {
            "current":
                current["settlement_rate"],
            "previous":
                previous["settlement_rate"],
            "change":
                calculate_rate_change(
                    current["settlement_rate"],
                    previous["settlement_rate"],
                ),
        },

        "cash_collection_rate": {
            "current":
                current["cash_collection_rate"],
            "previous":
                previous["cash_collection_rate"],
            "change":
                calculate_rate_change(
                    current["cash_collection_rate"],
                    previous["cash_collection_rate"],
                ),
        },

        "transaction_count": calculate_change(
            current["transaction_count"],
            previous["transaction_count"],
        ),

        "average_transaction": calculate_change(
            current["average_transaction"],
            previous["average_transaction"],
        ),
    }


# ============================================================
# MANAGEMENT ANALYSIS
# ============================================================

def get_management_analysis(
    current,
    previous,
):

    if current is None:

        return {
            "headline":
                "No financial data available.",
            "points": [],
        }

    gross = money(
        current.get("gross_invoiced")
    )

    cash = money(
        current.get("cash_collections")
    )

    credits = money(
        current.get("credits_applied")
    )

    outstanding = money(
        current.get("outstanding")
    )

    overpayment = money(
        current.get("overpayment_credit")
    )

    settlement = to_decimal(
        current.get("settlement_rate")
    )

    cash_rate = to_decimal(
        current.get("cash_collection_rate")
    )

    points = []

    if gross == ZERO:

        headline = (
            "No invoiced financial activity "
            "is recorded for the selected semester."
        )

    elif outstanding > ZERO:

        headline = (
            "The selected semester has an "
            "outstanding student balance."
        )

    elif overpayment > ZERO:

        headline = (
            "The selected semester is fully settled "
            "and has a credit or overpayment position."
        )

    else:

        headline = (
            "The selected semester is fully settled."
        )

    if gross > ZERO:

        points.append(
            f"Gross invoiced value is "
            f"KSh {gross:,.2f}."
        )

    points.append(
        f"Posted cash collections are "
        f"KSh {cash:,.2f}, representing "
        f"{cash_rate:.1f}% of gross invoicing."
    )

    if credits > ZERO:

        points.append(
            f"Credits applied against current invoices "
            f"total KSh {credits:,.2f}."
        )

    if outstanding > ZERO:

        points.append(
            f"Outstanding invoice balances total "
            f"KSh {outstanding:,.2f}. "
            f"Settlement stands at "
            f"{settlement:.1f}%."
        )

    else:

        points.append(
            f"There is no positive outstanding balance. "
            f"Settlement stands at "
            f"{settlement:.1f}%."
        )

    if overpayment > ZERO:

        points.append(
            f"The semester has a credit/overpayment "
            f"position of KSh {overpayment:,.2f}."
        )

    if previous is not None:

        gross_change = calculate_change(
            current["gross_invoiced"],
            previous["gross_invoiced"],
        )

        cash_change = calculate_change(
            current["cash_collections"],
            previous["cash_collections"],
        )

        outstanding_change = calculate_change(
            current["outstanding"],
            previous["outstanding"],
        )

        if gross_change["percent"] is not None:

            points.append(
                f"Gross invoicing changed by "
                f"{gross_change['percent']:.1f}% "
                f"from the previous semester."
            )

        if cash_change["percent"] is not None:

            points.append(
                f"Cash collections changed by "
                f"{cash_change['percent']:.1f}% "
                f"from the previous semester."
            )

        if outstanding_change["percent"] is not None:

            points.append(
                f"Outstanding balances changed by "
                f"{outstanding_change['percent']:.1f}% "
                f"from the previous semester."
            )

    return {
        "headline": headline,
        "points": points,
    }


# ============================================================
# HISTORICAL PERFORMANCE
# ============================================================

def get_historical_performance(
    user,
    department_id=None,
    programme_id=None,
):

    semesters = (
        get_all_semesters(user)
        .order_by(
            "-start_date",
            "-id",
        )
    )

    historical = []

    for semester in semesters:

        metrics = calculate_semester_metrics(
            user,
            semester,
            department_id=department_id,
            programme_id=programme_id,
        )

        academic_year_name = "-"

        if semester.academic_year:

            academic_year_name = (
                semester.academic_year.year_name
            )

        historical.append(
            {
                "academic_year":
                    academic_year_name,

                "semester":
                    semester.semester_name,

                "semester_id":
                    semester.id,

                "gross_invoiced":
                    metrics["gross_invoiced"],

                "cash_collections":
                    metrics["cash_collections"],

                "credits_applied":
                    metrics["credits_applied"],

                "outstanding":
                    metrics["outstanding"],

                "overpayment_credit":
                    metrics["overpayment_credit"],

                "settlement_rate":
                    metrics["settlement_rate"],

                "cash_collection_rate":
                    metrics["cash_collection_rate"],

                "transaction_count":
                    metrics["transaction_count"],

                "average_transaction":
                    metrics["average_transaction"],
            }
        )

    return historical


# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================

def get_department_performance(
    user,
    semester,
):

    if semester is None:
        return []

    invoices = get_semester_invoices(
        user,
        semester,
    )

    department_ids = (
        invoices
        .values_list(
            "student__programme__course__department_id",
            flat=True,
        )
        .distinct()
    )

    posted_status = (
        get_posted_payment_status()
    )

    performance = []

    for department_id in department_ids:

        if department_id is None:
            continue

        department_invoices = invoices.filter(
            student__programme__course__department_id=
            department_id
        )

        summary = department_invoices.aggregate(
            gross=Sum("invoice_total"),
            balance=Sum("balance_cached"),
            credits=Sum("credit_applied"),
        )

        gross = money(
            summary["gross"]
        )

        raw_balance = money(
            summary["balance"]
        )

        credits = money(
            summary["credits"]
        )

        if raw_balance > ZERO:

            outstanding = raw_balance
            overpayment = ZERO

        elif raw_balance < ZERO:

            outstanding = ZERO
            overpayment = abs(
                raw_balance
            )

        else:

            outstanding = ZERO
            overpayment = ZERO

        cash = money(
            Payment.objects
            .filter(
                invoice__in=department_invoices,
                posting_status=posted_status,
                is_reversed=False,
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
        )

        if gross > ZERO:

            settlement = (
                (gross - outstanding)
                / gross
                * HUNDRED
            )

            settlement = max(
                ZERO,
                min(
                    HUNDRED,
                    settlement,
                ),
            )

            cash_rate = (
                cash
                / gross
                * HUNDRED
            )

        else:

            settlement = ZERO
            cash_rate = ZERO

        department = (
            department_invoices
            .select_related(
                "student__programme__course__department"
            )
            .first()
        )

        if department:

            department_obj = (
                department
                .student
                .programme
                .course
                .department
            )

            department_code = (
                department_obj.code
                or "-"
            )

            department_name = (
                department_obj.name
                or "-"
            )

        else:

            department_code = "-"
            department_name = "-"

        performance.append(
            {
                "department_id":
                    department_id,

                "department_code":
                    department_code,

                "department_name":
                    department_name,

                "gross_invoiced":
                    money(gross),

                "cash_collections":
                    money(cash),

                "credits_applied":
                    money(credits),

                "outstanding":
                    money(outstanding),

                "overpayment_credit":
                    money(overpayment),

                "settlement_rate":
                    percentage(settlement),

                "cash_collection_rate":
                    percentage(cash_rate),
            }
        )

    performance.sort(
        key=lambda row: (
            row["department_name"] or ""
        )
    )

    return performance


# ============================================================
# POSTED TRANSACTIONS
# ============================================================

def get_posted_transactions(
    user,
    semester,
    department_id=None,
    programme_id=None,
):

    if semester is None:
        return Payment.objects.none()

    invoices = get_semester_invoices(
        user,
        semester,
        department_id=department_id,
        programme_id=programme_id,
    )

    posted_status = (
        get_posted_payment_status()
    )

    return (
        Payment.objects
        .filter(
            invoice__in=invoices,
            posting_status=posted_status,
            is_reversed=False,
        )
        .select_related(
            "invoice",
            "invoice__student",
            "invoice__student__programme",
            "invoice__student__programme__course",
            "invoice__student__programme__course__department",
            "received_by",
        )
        .order_by(
            "-payment_date",
            "-id",
        )
    )


# ============================================================
# COMPLETE FINANCIAL TRANSACTIONS REPORT
# ============================================================

def get_financial_transactions_report(
    user,
    current_semester=None,
    department_id=None,
    programme_id=None,
):

    if current_semester is None:

        current_semester = (
            get_current_semester(user)
        )

    current = calculate_semester_metrics(
        user,
        current_semester,
        department_id=department_id,
        programme_id=programme_id,
    )

    previous_semester = get_previous_semester(
        user,
        current_semester,
    )

    if previous_semester is not None:

        previous = calculate_semester_metrics(
            user,
            previous_semester,
            department_id=department_id,
            programme_id=programme_id,
        )

    else:

        previous = None

    comparison = build_comparison(
        current,
        previous,
    )

    historical = get_historical_performance(
        user,
        department_id=department_id,
        programme_id=programme_id,
    )

    department_performance = (
        get_department_performance(
            user,
            current_semester,
        )
    )

    transactions = get_posted_transactions(
        user,
        current_semester,
        department_id=department_id,
        programme_id=programme_id,
    )

    return {
        "current":
            current,

        "previous":
            previous,

        "comparison":
            comparison,

        "historical":
            historical,

        "department_performance":
            department_performance,

        "transactions":
            transactions,

        "current_semester":
            current_semester,

        "previous_semester":
            previous_semester,

        "department_id":
            department_id,

        "programme_id":
            programme_id,
    }


