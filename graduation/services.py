from students.models import (
    SemesterEnrollment,
    Registration,
    Result,
    Unit,
)

from finance.models import FinancialClearance


# ==========================================================
# Enrollment Helpers
# ==========================================================

def get_student_enrollments(student):
    """
    Return every semester enrollment for a student.
    """

    return (
        SemesterEnrollment.objects
        .filter(student=student)
        .select_related(
            "academic_year",
            "semester",
            "study_level",
        )
        .order_by(
            "academic_year",
            "semester",
        )
    )


def get_completed_study_levels(student):
    """
    Return all study levels the student has reached.

    Graduation must evaluate the whole programme,
    not only the current study level.
    """

    return (
        get_student_enrollments(student)
        .values_list(
            "study_level",
            flat=True,
        )
        .distinct()
    )


def get_required_units(student):
    """
    Return every curriculum unit belonging
    to the student's programme.

    Uses all study levels completed.
    """

    study_levels = get_completed_study_levels(student)

    return (
        Unit.objects
        .filter(
            course__programme=student.programme,
            course__study_level__in=study_levels,
        )
        .select_related(
            "course",
            "course__semester",
        )
        .distinct()
        .order_by(
            "course__study_level",
            "course__semester",
            "unit_code",
        )
    )


# ==========================================================
# Academic Assessment
# ==========================================================

def academic_assessment(student):
    """
    Academic graduation assessment.

    Rules

    • Student must have semester enrollments.

    • Student must have curriculum.

    • Student must register every required unit.

    • Every registered unit must have a result.

    • Every result must be approved.

    • Every unit must be passed.
    """

    summary = {

        "required_units": 0,

        "passed_units": 0,

        "failed_units": 0,

        "missing_results": 0,

        "missing_units": 0,

        "status": False,

        "issues": [],
    }

    enrollments = get_student_enrollments(student)

    # -----------------------------------
    # No enrollments
    # -----------------------------------

    if not enrollments.exists():

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    # -----------------------------------
    # Curriculum
    # -----------------------------------

    required_units = get_required_units(student)

    if not required_units.exists():

        summary["issues"].append(

            "No curriculum has been configured "
            "for the student's programme."

        )

        return summary

    summary["required_units"] = required_units.count()

    # -----------------------------------
    # Registrations
    # -----------------------------------

    registrations = Registration.objects.filter(
        enrollment__in=enrollments
    )

    if not registrations.exists():

        summary["issues"].append(
            "Student has not registered any units."
        )

        return summary

    # -----------------------------------
    # Check every curriculum unit
    # -----------------------------------

    for unit in required_units:

        registration = registrations.filter(
            unit=unit
        ).first()

        if not registration:

            summary["missing_units"] += 1

            summary["issues"].append(
                f"{unit} has never been registered."
            )

            continue

        result = Result.objects.filter(
            enrollment=registration.enrollment,
            unit=unit,
        ).first()

        if not result:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"No result found for {unit}."
            )

            continue

        if not result.is_approved:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"Result for {unit} has not been approved."
            )

            continue

        if result.remarks == "FAIL":

            summary["failed_units"] += 1

            summary["issues"].append(
                f"Failed {unit}."
            )

            continue

        summary["passed_units"] += 1

    # -----------------------------------
    # Final academic decision
    # -----------------------------------

    summary["status"] = (

        summary["required_units"] > 0

        and

        summary["passed_units"]
        == summary["required_units"]

        and

        summary["failed_units"] == 0

        and

        summary["missing_results"] == 0

        and

        summary["missing_units"] == 0

    )

    return summary

# ==========================================================
# Financial Assessment
# ==========================================================

def finance_assessment(student):
    """
    Check financial graduation clearance.

    Every semester enrollment must have a
    Financial Clearance record and the
    graduation clearance flag must be True.
    """

    summary = {
        "status": False,
        "issues": [],
    }

    enrollments = get_student_enrollments(student)

    if not enrollments.exists():

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    summary["status"] = True

    for enrollment in enrollments:

        try:

            clearance = enrollment.financial_clearance

        except FinancialClearance.DoesNotExist:

            summary["status"] = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "has no financial clearance record."
            )

            continue

        if not clearance.graduation_cleared:

            summary["status"] = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "graduation financial clearance pending."
            )

    return summary


# ==========================================================
# Progression Assessment
# ==========================================================

def progression_assessment(student):
    """
    Check programme completion.

    Every semester enrollment must have
    status='completed'.
    """

    summary = {
        "status": False,
        "issues": [],
    }

    enrollments = get_student_enrollments(student)

    if not enrollments.exists():

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    summary["status"] = True

    for enrollment in enrollments:

        if enrollment.status != "completed":

            summary["status"] = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "is not completed."
            )

    return summary


# ==========================================================
# Master Graduation Assessment
# ==========================================================

def graduation_assessment(student):
    """
    Production Graduation Eligibility Engine.

    This is the ONLY function that should be
    called by:

    • Graduation
    • Transcript
    • Certificate
    • Alumni
    • Graduation Approval
    """

    academic = academic_assessment(student)

    finance = finance_assessment(student)

    progression = progression_assessment(student)

    eligible = (

        academic["status"]

        and

        finance["status"]

        and

        progression["status"]

    )

    issues = []

    issues.extend(
        academic["issues"]
    )

    issues.extend(
        finance["issues"]
    )

    issues.extend(
        progression["issues"]
    )

    return {

        "eligible": eligible,

        "academic": academic,

        "finance": finance,

        "progression": progression,

        "issues": issues,

    }


# ==========================================================
# Backward Compatibility
# ==========================================================

def graduation_eligibility(student):
    """
    Temporary compatibility wrapper.

    Older views can still call
    graduation_eligibility().
    """

    return graduation_assessment(student)