"""
Student academic services.
"""

from django.db import transaction
from students.models import Result, ResultBatch, Registration
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


def student_has_passed_unit(student, unit):
    """
    Returns True if the student has a published PASS
    for the given unit.
    """

    return Result.objects.filter(
        enrollment__student=student,
        unit_offering__unit=unit,
        remarks="PASS",
        batch__status=ResultBatch.PUBLISHED,
    ).exists()


def get_outstanding_supplementary_units(enrollment):
    """
    Returns all failed published units that
    have not yet been passed.

    These units will automatically be
    registered as SUPPLEMENTARY in the
    student's next semester.
    """

    failed_results = (
        Result.objects.filter(
            enrollment__student=enrollment.student,
            remarks="FAIL",
            batch__status=ResultBatch.PUBLISHED,
        )
        .select_related(
            "unit_offering__unit",
        )
        .order_by(
            "unit_offering__unit__code",
        )
    )

    outstanding = []

    processed = set()

    for result in failed_results:

        unit = result.unit_offering.unit

        # Prevent duplicate units
        if unit.id in processed:
            continue

        processed.add(unit.id)

        # Ignore units already passed later
        if Result.objects.filter(
            enrollment__student=enrollment.student,
            unit_offering__unit=unit,
            remarks="PASS",
            batch__status=ResultBatch.PUBLISHED,
        ).exists():
            continue

        # Ignore units already registered
        if Registration.objects.filter(
            enrollment=enrollment,
            unit=unit,
        ).exists():
            continue

        outstanding.append(unit)

    return outstanding

def get_failed_units(enrollment):
    """
    Return all failed published results
    for one semester enrollment.
    """

    return (
        Result.objects.filter(
            enrollment=enrollment,
            remarks="FAIL",
            batch__status=ResultBatch.PUBLISHED,
        )
        .select_related(
            "unit_offering__unit",
        )
    )

def get_outstanding_units_for_programme_year(student, programme, year):
    """
    Returns all units from a programme year that
    the student has never passed.
    """

    registrations = (
        Registration.objects
        .filter(
            enrollment__student=student,
            enrollment__programme=programme,
            enrollment__programme_level__year=year,
            status=Registration.REGISTERED,
        )
        .select_related("unit")
        .distinct()
    )

    outstanding = []

    for registration in registrations:

        unit = registration.registered_unit

        if unit and not student_has_passed_unit(
            student,
            unit,
        ):

            outstanding.append(unit)

    return outstanding


def validate_year_boundary_progression(
    enrollment,
    next_level,
):
    """
    A student may carry failed units within the
    same programme year.

    However, before entering the next programme
    year, every unit from the previous year must
    have been passed.
    """

    current_year = (
        enrollment.programme_level.year
    )

    if next_level.year == current_year:

        return

    outstanding = (
        get_outstanding_units_for_programme_year(
            enrollment.student,
            enrollment.programme,
            current_year,
        )
    )

    if not outstanding:

        return

    codes = ", ".join(
        unit.code
        for unit in outstanding
    )

    raise ValueError(
        (
            f"Cannot progress to "
            f"Year {next_level.year}. "
            f"The following programme year "
            f"units are still outstanding: "
            f"units: {codes}."
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

    validate_year_boundary_progression(
    enrollment,
    next_level,
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