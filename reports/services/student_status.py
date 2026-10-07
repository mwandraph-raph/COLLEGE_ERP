"""
XORADEX EDUCORE ERP
STUDENT STATUS REPORT SERVICE

Provides role-aware student status summaries.
"""

from django.db.models import Count

from students.models import Student


def get_student_status_students(user):
    """
    Return students visible to the current user.

    HOD users are restricted to their department.
    Other authorised report roles see all students.
    """

    students = Student.objects.select_related(
        "programme",
        "programme__course",
        "programme__course__department",
    )

    if user.groups.filter(name="HOD").exists():
        students = students.filter(
            programme__course__department__hod=user
        )

    return students


def get_student_status_summary(user):
    """
    Build the Student Status Report.
    """

    students = get_student_status_students(user)

    total_students = students.count()

    status_rows = (
        students
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    statuses = []

    for row in status_rows:

        total = row["total"]

        percentage = (
            (total / total_students) * 100
            if total_students
            else 0
        )

        if row["status"] == Student.ACTIVE:
            label = "Active"
        elif row["status"] == Student.INACTIVE:
            label = "Inactive"
        else:
            label = row["status"] or "Not specified"

        statuses.append({
            "code": row["status"],
            "label": label,
            "total": total,
            "percentage": round(percentage, 1),
        })

    active_students = students.filter(
        status=Student.ACTIVE
    ).count()

    inactive_students = students.filter(
        status=Student.INACTIVE
    ).count()

    return {
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
        "statuses": statuses,
    }