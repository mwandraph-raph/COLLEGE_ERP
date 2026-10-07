"""
XORADEX EDUCORE ERP
ENROLLMENT SUMMARY SERVICE

Provides role-aware student enrollment summaries.
"""

from django.db.models import Count

from students.models import Student


def get_enrollment_students(user):
    """
    Return the student queryset visible to the current user.

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


def get_enrollment_summary(user):
    """
    Build the complete enrollment summary.
    """

    students = get_enrollment_students(user)

    total_students = students.count()

    active_students = students.filter(
        status=Student.ACTIVE
    ).count()

    inactive_students = students.filter(
        status=Student.INACTIVE
    ).count()

    departments = (
        students
        .values(
            "programme__course__department_id",
            "programme__course__department__code",
            "programme__course__department__name",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "programme__course__department__name"
        )
    )

    courses = (
        students
        .values(
            "programme__course_id",
            "programme__course__code",
            "programme__course__name",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "programme__course__name"
        )
    )

    programmes = (
        students
        .values(
            "programme_id",
            "programme__code",
            "programme__name",
            "programme__award",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "programme__name"
        )
    )

    awards = (
        students
        .values(
            "programme__award"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "programme__award"
        )
    )

    gender = (
        students
        .values(
            "gender"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "gender"
        )
    )

    status = (
        students
        .values(
            "status"
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "status"
        )
    )

    return {
        "total_students": total_students,
        "active_students": active_students,
        "inactive_students": inactive_students,
        "department_count": departments.count(),
        "course_count": courses.count(),
        "programme_count": programmes.count(),

        "departments": departments,
        "courses": courses,
        "programmes": programmes,
        "awards": awards,
        "gender": gender,
        "status": status,
    }

