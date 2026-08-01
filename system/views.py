from datetime import date

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