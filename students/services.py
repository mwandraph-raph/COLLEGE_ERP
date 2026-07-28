"""
Student academic services.
"""

from django.db import transaction
from students.models import Result
from students.models import (
    Semester,
    SemesterEnrollment,
    ProgressionLog,
)


def get_next_academic_period(enrollment):
    """
    Determine the next Academic Year and Semester.

    Rules

    Semester 1 -> Semester 2 (same Academic Year)

    Semester 2 -> Semester 1 (next Academic Year)
    """

    current_semester = enrollment.semester

    # -----------------------------------
    # Semester 1 -> Semester 2
    # -----------------------------------

    if current_semester.semester_name == "Semester 1":

        next_semester = (
            Semester.objects.filter(
                academic_year=enrollment.academic_year,
                semester_name="Semester 2",
            ).first()
        )

        if next_semester:

            return (
                enrollment.academic_year,
                next_semester,
            )

    # -----------------------------------
    # Semester 2 -> Next Academic Year
    # -----------------------------------

    if current_semester.semester_name == "Semester 2":

        next_year = (
            enrollment.academic_year.__class__.objects
            .exclude(
                pk=enrollment.academic_year.pk,
            )
            .order_by(
                "year_name",
            )
            .first()
        )

        if next_year:

            next_semester = (
                Semester.objects.filter(
                    academic_year=next_year,
                    semester_name="Semester 1",
                ).first()
            )

            if next_semester:

                return (
                    next_year,
                    next_semester,
                )

    return (
        None,
        None,
    )


def validate_results_exist(enrollment):
    """
    Ensure every registered unit has a result.
    """

    registrations = (
        enrollment.registrations
        .filter(
            status="REGISTERED",
        )
    )

    total_registered = registrations.count()

    total_results = Result.objects.filter(
        enrollment=enrollment,
    ).count()

    if total_registered != total_results:

        raise ValueError(
            "Some registered units do not have results."
        )


def validate_results_published(enrollment):
    """
    Ensure all results have been published.
    """

    unpublished = Result.objects.filter(
        enrollment=enrollment,
    ).exclude(
        batch__status="published",
    )

    if unpublished.exists():

        raise ValueError(
            "Results have not yet been published."
        )


def validate_passed_units(enrollment):
    """
    Ensure the student has passed every registered unit.
    """

    failed_results = Result.objects.filter(
        enrollment=enrollment,
        remarks="FAIL",
    )

    if failed_results.exists():

        failed_units = ", ".join(
            failed_results.values_list(
                "unit_offering__unit__code",
                flat=True,
            )
        )

        raise ValueError(
            (
                "Student cannot progress. "
                "Failed units: "
                f"{failed_units}."
            )
        )


@transaction.atomic
def progress_student(
    enrollment,
    user=None,
):
    """
    Basic progression service.

    Validation will be added later.
    """
    validate_results_exist(
        enrollment
    )

    validate_results_published(
    enrollment
    )

    validate_results_exist(
    enrollment
    )

    validate_results_published(
        enrollment
    )

    validate_passed_units(
        enrollment
    )

    current_level = (
        enrollment.programme_level
    )

    next_level = (
        enrollment.programme.levels
        .filter(
            progression_order__gt=
            current_level.progression_order,
            is_active=True,
        )
        .order_by(
            "progression_order",
        )
        .first()
    )

    # -----------------------------
    # Final Programme Level
    # -----------------------------

    if next_level is None:

        enrollment.status = (
            SemesterEnrollment.COMPLETED
        )

        enrollment.save()

        ProgressionLog.objects.create(
            student=enrollment.student,
            from_enrollment=enrollment,
            action=ProgressionLog.COMPLETED,
            performed_by=user,
        )

        return enrollment

    # -----------------------------
    # Next Academic Period
    # -----------------------------

    next_year, next_semester = (
        get_next_academic_period(
            enrollment
        )
    )

    if (
        next_year is None
        or next_semester is None
    ):

        raise ValueError(
            "Next academic period has not been configured."
        )

    # Prevent duplicate enrollment

    if SemesterEnrollment.objects.filter(
        student=enrollment.student,
        academic_year=next_year,
        semester=next_semester,
    ).exists():

        raise ValueError(
            "Student is already enrolled in the next semester."
        )

    # -----------------------------
    # Create New Enrollment
    # -----------------------------

    new_enrollment = (
        SemesterEnrollment.objects.create(
            student=enrollment.student,
            programme=enrollment.programme,
            programme_level=next_level,
            academic_year=next_year,
            semester=next_semester,
            status=SemesterEnrollment.ENROLLED,
        )
    )

    # -----------------------------
    # Close Current Enrollment
    # -----------------------------

    enrollment.status = (
        SemesterEnrollment.PROGRESSED
    )

    enrollment.save()

    # -----------------------------
    # Audit Log
    # -----------------------------

    ProgressionLog.objects.create(
        student=enrollment.student,
        from_enrollment=enrollment,
        to_enrollment=new_enrollment,
        action=ProgressionLog.PROMOTED,
        performed_by=user,
    )

    return new_enrollment