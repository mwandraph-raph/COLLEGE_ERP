from students.models import (
    SemesterEnrollment,
    Registration,
)
from finance.models import FinancialClearance
from students.models import Result
from .models import Graduation

def get_student_enrollments(student):
    """
    Return every semester enrollment for the student.
    """
    return (
        SemesterEnrollment.objects
        .filter(student=student)
        .order_by(
            "academic_year",
            "semester"
        )
    )

def academic_requirements_met(student):
    """
    Check whether the student has
    completed all registered units.
    """

    registrations = Registration.objects.filter(
        enrollment__student=student
    )

    if not registrations.exists():
        return False, "No unit registrations found."

    for registration in registrations:

        try:
            result = Result.objects.get(
                enrollment=registration.enrollment,
                unit=registration.unit
            )

        except Result.DoesNotExist:

            return False, (
                f"Missing result for "
                f"{registration.unit}"
            )

        if not result.is_approved:

            return False, (
                f"{registration.unit} "
                "result not approved."
            )

        if result.remarks == "FAIL":

            return False, (
                f"Failed "
                f"{registration.unit}"
            )

    return True, "Academic requirements satisfied."

def finance_requirements_met(student):
    """
    Check graduation financial clearance.
    """

    enrollments = get_student_enrollments(student)

    for enrollment in enrollments:

        try:

            clearance = (
                enrollment.financial_clearance
            )

        except FinancialClearance.DoesNotExist:

            return False, (
                "Financial clearance "
                "record missing."
            )

        if not clearance.graduation_cleared:

            return False, (
                "Graduation financial "
                "clearance pending."
            )

    return True, "Financial requirements satisfied."

