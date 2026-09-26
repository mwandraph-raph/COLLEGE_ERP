from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    Q,
    Count,
    Max,
)
from django.shortcuts import render

from .models import ActivityLog
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from io import BytesIO
from django.utils import timezone
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from students.models import (
    Applicant,
    Department,
    Course,
    Programme,
    AcademicYear,
    Intake,
    Semester,
    ProgrammeLevel,
    Unit,
    Student,
    SemesterEnrollment,
    UnitOffering,
    Registration,
)

from finance.models import (
    StudentInvoice,
    Payment,
    Receipt,
)

from graduation.models import Graduation

User = get_user_model()

@login_required
def global_search(request):
    q = request.GET.get("q", "").strip()

    results = []

    if q:
        # =========================================================
        # STUDENTS
        # =========================================================
        students = Student.objects.filter(
            Q(admission_no__icontains=q) |
            Q(first_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(id_number__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q) |
            Q(programme__name__icontains=q) |
            Q(programme__code__icontains=q)
        ).select_related("programme").distinct()[:10]

        for student in students:
            results.append({
                "category": "Students",
                "title": student.full_name,
                "subtitle": (
                    f"{student.admission_no} • "
                    f"{student.programme.name if student.programme else 'No programme'}"
                ),
                "icon": "fa-user-graduate",
                "object": student,
                "url": "/semester-enrollments/",
            })

        # =========================================================
        # APPLICANTS
        # =========================================================
        applicants = Applicant.objects.filter(
            Q(application_no__icontains=q) |
            Q(first_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(id_number__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(email__icontains=q) |
            Q(programme__name__icontains=q) |
            Q(programme__code__icontains=q)
        ).select_related("programme").distinct()[:10]

        for applicant in applicants:
            full_name = " ".join(
                part for part in [
                    applicant.first_name,
                    applicant.middle_name,
                    applicant.last_name,
                ]
                if part
            )

            results.append({
                "category": "Applicants",
                "title": full_name,
                "subtitle": (
                    f"{applicant.application_no} • "
                    f"{applicant.programme.name if applicant.programme else 'No programme'}"
                ),
                "icon": "fa-file-signature",
                "object": applicant,
            })

        # =========================================================
        # PROGRAMMES
        # =========================================================
        programmes = Programme.objects.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(award__icontains=q) |
            Q(course__name__icontains=q) |
            Q(course__code__icontains=q)
        ).select_related("course").distinct()[:10]

        for programme in programmes:
            results.append({
                "category": "Programmes",
                "title": programme.name,
                "subtitle": (
                    f"{programme.code} • "
                    f"{programme.award} • "
                    f"{programme.course.name if programme.course else 'No course'}"
                ),
                "icon": "fa-book-open",
                "object": programme,
            })

        # =========================================================
        # COURSES
        # =========================================================
        courses = Course.objects.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(department__name__icontains=q) |
            Q(department__code__icontains=q)
        ).select_related("department").distinct()[:10]

        for course in courses:
            results.append({
                "category": "Courses",
                "title": course.name,
                "subtitle": (
                    f"{course.code} • "
                    f"{course.department.name if course.department else 'No department'}"
                ),
                "icon": "fa-layer-group",
                "object": course,
            })

        # =========================================================
        # DEPARTMENTS
        # =========================================================
        departments = Department.objects.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q)
        ).distinct()[:10]

        for department in departments:
            results.append({
                "category": "Departments",
                "title": department.name,
                "subtitle": department.code,
                "icon": "fa-building",
                "object": department,
            })

        # =========================================================
        # UNITS
        # =========================================================
        units = Unit.objects.filter(
            Q(code__icontains=q) |
            Q(name__icontains=q) |
            Q(programme_level__name__icontains=q) |
            Q(programme_level__programme__name__icontains=q) |
            Q(programme_level__programme__code__icontains=q)
        ).select_related(
            "programme_level",
            "programme_level__programme"
        ).distinct()[:10]

        for unit in units:
            programme = unit.programme_level.programme

            results.append({
                "category": "Units",
                "title": unit.name,
                "subtitle": (
                    f"{unit.code} • "
                    f"{programme.name if programme else 'No programme'} • "
                    f"{unit.programme_level.name if unit.programme_level else ''}"
                ),
                "icon": "fa-book",
                "object": unit,
            })

        # =========================================================
        # SEMESTER ENROLLMENTS
        # =========================================================
        enrollments = SemesterEnrollment.objects.filter(
            Q(student__admission_no__icontains=q) |
            Q(student__first_name__icontains=q) |
            Q(student__middle_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(programme__name__icontains=q) |
            Q(programme__code__icontains=q) |
            Q(academic_year__year_name__icontains=q) |
            Q(semester__semester_name__icontains=q) |
            Q(status__icontains=q)
        ).select_related(
            "student",
            "programme",
            "academic_year",
            "semester",
            "programme_level",
        ).distinct()[:10]

        for enrollment in enrollments:
            results.append({
                "category": "Enrollments",
                "title": enrollment.student.full_name,
                "subtitle": (
                    f"{enrollment.student.admission_no} • "
                    f"{enrollment.academic_year.year_name} • "
                    f"{enrollment.semester.semester_name} • "
                    f"{enrollment.status}"
                ),
                "icon": "fa-user-check",
                "object": enrollment,
            })

        # =========================================================
        # UNIT OFFERINGS
        # =========================================================
        offerings = UnitOffering.objects.filter(
            Q(unit__code__icontains=q) |
            Q(unit__name__icontains=q) |
            Q(academic_year__year_name__icontains=q) |
            Q(semester__semester_name__icontains=q) |
            Q(programme_level__name__icontains=q) |
            Q(programme_level__programme__name__icontains=q)
        ).select_related(
            "unit",
            "academic_year",
            "semester",
            "programme_level",
            "programme_level__programme",
        ).distinct()[:10]

        for offering in offerings:
            results.append({
                "category": "Unit Offerings",
                "title": f"{offering.unit.code} - {offering.unit.name}",
                "subtitle": (
                    f"{offering.academic_year.year_name} • "
                    f"{offering.semester.semester_name} • "
                    f"{offering.programme_level.name}"
                ),
                "icon": "fa-chalkboard",
                "object": offering,
            })

        # =========================================================
        # REGISTRATIONS
        # =========================================================
        registrations = Registration.objects.filter(
            Q(enrollment__student__admission_no__icontains=q) |
            Q(enrollment__student__first_name__icontains=q) |
            Q(enrollment__student__middle_name__icontains=q) |
            Q(enrollment__student__last_name__icontains=q) |
            Q(unit_offering__unit__code__icontains=q) |
            Q(unit_offering__unit__name__icontains=q) |
            Q(unit__code__icontains=q) |
            Q(unit__name__icontains=q) |
            Q(status__icontains=q)
        ).select_related(
            "enrollment__student",
            "unit_offering__unit",
            "unit",
        ).distinct()[:10]

        for registration in registrations:
            unit = registration.registered_unit

            results.append({
                "category": "Registrations",
                "title": registration.enrollment.student.full_name,
                "subtitle": (
                    f"{registration.enrollment.student.admission_no} • "
                    f"{unit.code if unit else 'No unit'} • "
                    f"{registration.status}"
                ),
                "icon": "fa-clipboard-check",
                "object": registration,
            })

        # =========================================================
        # LECTURERS
        # =========================================================
        lecturers = User.objects.filter(
            groups__name="Lecturer"
        ).filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        ).distinct()[:10]

        for lecturer in lecturers:
            full_name = (
                lecturer.get_full_name()
                or lecturer.username
            )

            results.append({
                "category": "Lecturers",
                "title": full_name,
                "subtitle": (
                    f"{lecturer.username}"
                    + (f" • {lecturer.email}" if lecturer.email else "")
                ),
                "icon": "fa-chalkboard-teacher",
                "object": lecturer,
            })

        # =========================================================
        # INVOICES
        # =========================================================
        invoices = StudentInvoice.objects.filter(
            Q(invoice_number__icontains=q) |
            Q(student__admission_no__icontains=q) |
            Q(student__first_name__icontains=q) |
            Q(student__middle_name__icontains=q) |
            Q(student__last_name__icontains=q)
        ).select_related(
            "student"
        ).distinct()[:10]

        for invoice in invoices:
            results.append({
                "category": "Invoices",
                "title": invoice.invoice_number,
                "subtitle": (
                    f"{invoice.student.full_name} • "
                    f"Balance: KSh {invoice.balance:,.2f} • "
                    f"{invoice.status}"
                ),
                "icon": "fa-file-invoice-dollar",
                "object": invoice,
            })

        # =========================================================
        # PAYMENTS
        # =========================================================
        payments = Payment.objects.filter(
            Q(payment_number__icontains=q) |
            Q(reference_number__icontains=q) |
            Q(invoice__invoice_number__icontains=q) |
            Q(invoice__student__admission_no__icontains=q) |
            Q(invoice__student__first_name__icontains=q) |
            Q(invoice__student__middle_name__icontains=q) |
            Q(invoice__student__last_name__icontains=q)
        ).select_related(
            "invoice",
            "invoice__student",
        ).distinct()[:10]

        for payment in payments:
            results.append({
                "category": "Payments",
                "title": payment.payment_number,
                "subtitle": (
                    f"{payment.invoice.student.full_name} • "
                    f"KSh {payment.amount:,.2f} • "
                    f"{payment.reference_number or 'No reference'}"
                ),
                "icon": "fa-money-bill-wave",
                "object": payment,
            })

        # =========================================================
        # RECEIPTS
        # =========================================================
        receipts = Receipt.objects.filter(
            Q(receipt_number__icontains=q) |
            Q(payment__payment_number__icontains=q) |
            Q(payment__invoice__invoice_number__icontains=q) |
            Q(payment__invoice__student__admission_no__icontains=q) |
            Q(payment__invoice__student__first_name__icontains=q) |
            Q(payment__invoice__student__middle_name__icontains=q) |
            Q(payment__invoice__student__last_name__icontains=q)
        ).select_related(
            "payment",
            "payment__invoice",
            "payment__invoice__student",
        ).distinct()[:10]

        for receipt in receipts:
            results.append({
                "category": "Receipts",
                "title": receipt.receipt_number,
                "subtitle": (
                    f"{receipt.payment.invoice.student.full_name} • "
                    f"{receipt.payment.payment_number}"
                ),
                "icon": "fa-receipt",
                "object": receipt,
            })

        # =========================================================
        # GRADUATION
        # =========================================================
        graduations = Graduation.objects.filter(
            Q(certificate_number__icontains=q) |
            Q(student__admission_no__icontains=q) |
            Q(student__first_name__icontains=q) |
            Q(student__middle_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(status__icontains=q)
        ).select_related(
            "student",
            "academic_year",
        ).distinct()[:10]

        for graduation in graduations:
            results.append({
                "category": "Graduation",
                "title": graduation.student.full_name,
                "subtitle": (
                    f"{graduation.certificate_number} • "
                    f"{graduation.status}"
                ),
                "icon": "fa-graduation-cap",
                "object": graduation,
            })

        # =========================================================
        # ACADEMIC YEARS
        # =========================================================
        academic_years = AcademicYear.objects.filter(
            Q(year_name__icontains=q)
        ).distinct()[:10]

        for year in academic_years:
            results.append({
                "category": "Academic Years",
                "title": year.year_name,
                "subtitle": (
                    "Registration Open"
                    if year.registration_open
                    else "Registration Closed"
                ),
                "icon": "fa-calendar-alt",
                "object": year,
            })

        # =========================================================
        # INTAKES
        # =========================================================
        intakes = Intake.objects.filter(
            Q(name__icontains=q) |
            Q(academic_year__year_name__icontains=q)
        ).select_related(
            "academic_year"
        ).distinct()[:10]

        for intake in intakes:
            results.append({
                "category": "Intakes",
                "title": intake.name,
                "subtitle": (
                    f"{intake.academic_year.year_name} • "
                    f"{'Open' if intake.is_open else 'Closed'}"
                ),
                "icon": "fa-calendar-plus",
                "object": intake,
            })

        # =========================================================
        # SEMESTERS
        # =========================================================
        semesters = Semester.objects.filter(
            Q(semester_name__icontains=q) |
            Q(academic_year__year_name__icontains=q)
        ).select_related(
            "academic_year"
        ).distinct()[:10]

        for semester in semesters:
            results.append({
                "category": "Semesters",
                "title": semester.semester_name,
                "subtitle": (
                    f"{semester.academic_year.year_name} • "
                    f"{'Active' if semester.is_active else 'Inactive'}"
                ),
                "icon": "fa-calendar-week",
                "object": semester,
            })

    context = {
        "q": q,
        "results": results,
        "result_count": len(results),
    }

    return render(
        request,
        "system/global_search.html",
        context
    )

@login_required
@permission_required(
    "system.view_activitylog",
    raise_exception=True,
)
def activity_list(request):

    activities = (
        ActivityLog.objects
        .select_related("user")
        .order_by("-created_at")
    )


    # =====================================
    # SEARCH
    # =====================================

    search = request.GET.get("search")

    if search:

        activities = activities.filter(
            Q(description__icontains=search)
            |
            Q(object_name__icontains=search)
            |
            Q(ip_address__icontains=search)
            |
            Q(user__username__icontains=search)
        )


    # =====================================
    # MODULE FILTER
    # =====================================

    module = request.GET.get("module")

    if module:

        activities = activities.filter(
            module=module
        )



    # =====================================
    # ACTION FILTER
    # =====================================

    action = request.GET.get("action")

    if action:

        activities = activities.filter(
            action=action
        )



    # =====================================
    # SEVERITY FILTER
    # =====================================

    severity = request.GET.get("severity")

    if severity:

        activities = activities.filter(
            severity=severity
        )



    # =====================================
    # USER FILTER
    # =====================================

    user = request.GET.get("user")

    if user:

        activities = activities.filter(
            user_id=user
        )



    # =====================================
    # DATE FILTER
    # =====================================

    activity_date = request.GET.get("date")

    start_date = request.GET.get("start_date")

    end_date = request.GET.get("end_date")



    if activity_date:

        activities = activities.filter(
            created_at__date=activity_date
        )


    if start_date:

        activities = activities.filter(
            created_at__date__gte=start_date
        )


    if end_date:

        activities = activities.filter(
            created_at__date__lte=end_date
        )



    # =====================================
    # STATISTICS
    # =====================================

    total_activities = activities.count()


    today = date.today()


    critical_count = (
        ActivityLog.objects
        .filter(
            severity=ActivityLog.CRITICAL
        )
        .count()
    )



    today_count = (
        ActivityLog.objects
        .filter(
            created_at__date=today
        )
        .count()
    )



    active_users = (
        ActivityLog.objects
        .filter(
            user__isnull=False
        )
        .values(
            "user"
        )
        .distinct()
        .count()
    )



    # =====================================
    # SECURITY ANALYTICS
    # =====================================


    most_active_user = (
        ActivityLog.objects
        .values(
            "user__username"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
        .first()
    )



    most_active_module = (
        ActivityLog.objects
        .values(
            "module"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")
        .first()
    )



    login_count = (
        ActivityLog.objects
        .filter(
            action=ActivityLog.LOGIN
        )
        .count()
    )



    delete_count = (
        ActivityLog.objects
        .filter(
            action=ActivityLog.DELETE
        )
        .count()
    )



    # =====================================
    # AUDIT INTEGRITY
    # =====================================


    tampered_count = 0


    for log in ActivityLog.objects.all():

        if not log.verify_integrity():

            tampered_count += 1



    verified_count = (
        ActivityLog.objects.count()
        -
        tampered_count
    )



    # =====================================
    # PAGINATION
    # =====================================


    paginator = Paginator(
        activities,
        25
    )


    page_number = request.GET.get(
        "page",
        1
    )


    page_obj = paginator.get_page(
        page_number
    )



    # Verify displayed records

    for activity in page_obj:

        activity.is_verified = (
            activity.verify_integrity()
        )


        activity.integrity_status = (

            "Verified"

            if activity.is_verified

            else "Tampered"

        )



    # =====================================
    # CHART DATA
    # =====================================


    action_chart = list(

        ActivityLog.objects
        .values(
            "action"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")

    )



    module_chart = list(

        ActivityLog.objects
        .values(
            "module"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")

    )



    severity_chart = list(

        ActivityLog.objects
        .values(
            "severity"
        )
        .annotate(
            total=Count("id")
        )
        .order_by("-total")

    )



    # =====================================
    # ACTIVITY TIMELINE
    # =====================================


    timeline = (
        activities
        .select_related("user")
        .order_by("-created_at")[:10]
    )


    # =====================================
    # CONTEXT
    # =====================================

    context = {

        # TABLE

        "activities": page_obj,

        "page_obj": page_obj,


        # KPI
        "total_activities":
            total_activities,

        "critical_count":
            critical_count,

        "today_count":
            today_count,

        "active_users":
            active_users,

        "verified_count":
            verified_count,

        "tampered_count":
            tampered_count,


        # SECURITY ANALYTICS

        "most_active_user":
            most_active_user,


        "most_active_module":
            most_active_module,


        "login_count":
            login_count,


        "delete_count":
            delete_count,


        # CHARTS

        "action_chart":
            action_chart,

        "module_chart":
            module_chart,

        "severity_chart":
            severity_chart,

        # TIMELINE

        "timeline":
            timeline,


        # FILTERS

        "modules":
            ActivityLog.MODULE_CHOICES,


        "actions":
            ActivityLog.ACTION_CHOICES,


        "users":
            (
                ActivityLog.objects
                .filter(
                    user__isnull=False
                )
                .values(
                    "user__id",
                    "user__username"
                )
                .distinct()
            ),

    }


    return render(
        request,
        "system/activity.html",
        context
    )


@login_required
@permission_required(
    "system.view_activitylog",
    raise_exception=True,
)
@login_required
def activity_export_excel(request):

    activities = ActivityLog.objects.select_related(
        "user"
    ).all()


    # ==========================
    # APPLY SAME FILTERS
    # ==========================

    search = request.GET.get("search")

    if search:

        activities = activities.filter(

            Q(description__icontains=search)
            |
            Q(object_name__icontains=search)
            |
            Q(ip_address__icontains=search)
            |
            Q(user__username__icontains=search)

        )


    module = request.GET.get("module")

    if module:

        activities = activities.filter(
            module=module
        )


    action = request.GET.get("action")

    if action:

        activities = activities.filter(
            action=action
        )


    user = request.GET.get("user")

    if user:

        activities = activities.filter(
            user_id=user
        )


    activity_date = request.GET.get("date")

    if activity_date:

        activities = activities.filter(
            created_at__date=activity_date
        )



    # ==========================
    # CREATE EXCEL FILE
    # ==========================

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Activity Log"



    headers = [

        "Date",
        "User",
        "Module",
        "Action",
        "Severity",
        "Description",
        "Object",
        "IP Address"

    ]


    sheet.append(headers)



    # Header styling

    for cell in sheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )



    # Data rows

    for activity in activities:


        sheet.append([

            activity.created_at.strftime(
                "%d %b %Y %H:%M"
            ),


            activity.user.username
            if activity.user
            else "System",


            activity.module,


            activity.action,


            activity.severity,


            activity.description,


            activity.object_name,


            activity.ip_address
            or "-"

        ])




    # Auto width

    for column in sheet.columns:

        max_length = 0

        column_letter = column[0].column_letter


        for cell in column:

            if cell.value:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )


        sheet.column_dimensions[
            column_letter
        ].width = max_length + 3




    # Response

    response = HttpResponse(
        content_type=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    response["Content-Disposition"] = (
        'attachment; filename="xoradex_activity_log.xlsx"'
    )


    workbook.save(response)


    return response


@login_required
@permission_required(
    "system.view_activitylog",
    raise_exception=True,
)
@login_required
def activity_export_pdf(request):

    activities = ActivityLog.objects.select_related(
        "user"
    ).all()


    # ==========================
    # APPLY FILTERS
    # ==========================

    search = request.GET.get("search")

    if search:

        activities = activities.filter(
            Q(description__icontains=search)
            |
            Q(object_name__icontains=search)
            |
            Q(ip_address__icontains=search)
            |
            Q(user__username__icontains=search)
        )


    module = request.GET.get("module")

    if module:
        activities = activities.filter(
            module=module
        )


    action = request.GET.get("action")

    if action:
        activities = activities.filter(
            action=action
        )


    user = request.GET.get("user")

    if user:
        activities = activities.filter(
            user_id=user
        )


    activity_date = request.GET.get("date")

    if activity_date:

        activities = activities.filter(
            created_at__date=activity_date
        )



    # ==========================
    # CREATE PDF
    # ==========================

    buffer = BytesIO()


    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        title="Xoradex EduCore Activity Audit Report"
    )


    elements = []


    styles = getSampleStyleSheet()



    elements.append(
        Paragraph(
            "Xoradex EduCore",
            styles["Title"]
        )
    )


    elements.append(
        Paragraph(
            "System Activity Audit Report",
            styles["Heading2"]
        )
    )


    elements.append(
        Paragraph(
            f"Generated: {timezone.now():%d %B %Y %H:%M}",
            styles["Normal"]
        )
    )


    elements.append(
        Spacer(1, 20)
    )



    data = [

        [
            "Date",
            "User",
            "Module",
            "Action",
            "Severity",
            "Description",
            "Object",
            "IP"
        ]

    ]



    for activity in activities:


        data.append([

            activity.created_at.strftime(
                "%d-%m-%Y %H:%M"
            ),


            activity.user.username
            if activity.user
            else "System",


            activity.module,


            activity.action,


            activity.severity,


            activity.description,


            activity.object_name
            or "-",


            activity.ip_address
            or "-"

        ])




    table = Table(
        data,
        repeatRows=1
    )


    table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                colors.lightgrey
            ),

            (
                "GRID",
                (0,0),
                (-1,-1),
                0.5,
                colors.grey
            ),

            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "TOP"
            ),

        ])
    )


    elements.append(table)



    document.build(
        elements
    )


    pdf = buffer.getvalue()

    buffer.close()



    response = HttpResponse(
        pdf,
        content_type="application/pdf"
    )


    response["Content-Disposition"] = (
        'attachment; filename="xoradex_activity_audit.pdf"'
    )


    return response