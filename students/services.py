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
    Determine the next academic period based on the configured
    semester sequence.

    Semester sequence:
        Jan - March
        April - June
        July - September
        October - December

    Progression:
        1st semester -> 2nd semester
        2nd semester -> 3rd semester
        3rd semester -> 4th semester
        4th semester -> next academic year's 1st semester
    """

    current_year = enrollment.academic_year
    current_semester = enrollment.semester

    semester_order = {
        "Jan - March": 1,
        "April - June": 2,
        "July - September": 3,
        "October - December": 4,
    }

    current_order = semester_order.get(
        current_semester.semester_name
    )

    if current_order is None:
        return None, None

    # ==========================================================
    # NEXT SEMESTER IN SAME ACADEMIC YEAR
    # ==========================================================

    if current_order < 4:

        next_order = current_order + 1

        next_semester_name = next(
            (
                name
                for name, order in semester_order.items()
                if order == next_order
            ),
            None,
        )

        next_semester = (
            Semester.objects
            .filter(
                academic_year=current_year,
                semester_name=next_semester_name,
            )
            .first()
        )

        if next_semester:
            return current_year, next_semester

        return None, None

    # ==========================================================
    # OCTOBER - DECEMBER -> NEXT ACADEMIC YEAR
    # ==========================================================

    next_year = (
        current_year.__class__.objects
        .filter(
            year_name__gt=current_year.year_name,
        )
        .order_by(
            "year_name",
        )
        .first()
    )

    if not next_year:
        return None, None

    next_semester = (
        Semester.objects
        .filter(
            academic_year=next_year,
            semester_name="Jan - March",
        )
        .first()
    )

    if next_semester:
        return next_year, next_semester

    return None, None


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
    Progress a student to the next programme level.

    Progression requirements:

    1. All registered units must have results.
    2. All results must be published.
    3. The student's current semester invoice must be
       100% financially cleared.
    4. All units from the current programme year must be
       passed before crossing into the next programme year.
    5. The next academic period must be configured.
    6. Duplicate enrollment must not be created.

    Financial Rule
    --------------
    A student MUST have paid 100% of the financial obligation
    for the current semester before progression is allowed.

    Therefore:

        100%  -> progression allowed
        99.99% or below -> progression blocked

    The financial check is performed server-side here so that
    progression cannot be bypassed through the user interface.
    """

    # ==========================================================
    # 1. VALIDATE RESULTS
    # ==========================================================

    validate_results_exist(
        enrollment
    )

    # ==========================================================
    # 2. VALIDATE RESULTS PUBLICATION
    # ==========================================================

    validate_results_published(
        enrollment
    )

    # ==========================================================
    # 3. FINANCIAL CLEARANCE
    #
    # A student must have completely settled the invoice
    # belonging to THIS semester before progressing.
    # ==========================================================

    try:

        invoice = enrollment.invoice

    except Exception:

        raise ValueError(
            "Cannot progress this student because the current "
            "semester has no financial invoice."
        )

    payment_percentage = invoice.payment_percentage

    if payment_percentage < 100:

        raise ValueError(
            (
                "Cannot progress this student. "
                f"Financial clearance is {payment_percentage}%. "
                "The student must be 100% financially cleared "
                "for the current semester before progressing."
            )
        )

    # ==========================================================
    # 4. CURRENT PROGRAMME LEVEL
    # ==========================================================

    current_level = (
        enrollment.programme_level
    )

    # ==========================================================
    # 5. DETERMINE NEXT PROGRAMME LEVEL
    # ==========================================================

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

    # ==========================================================
    # 6. FINAL PROGRAMME LEVEL
    #
    # If there is no next programme level, the student has
    # completed the programme.
    # ==========================================================

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

    # ==========================================================
    # 7. YEAR BOUNDARY VALIDATION
    #
    # Failed units may be carried within the same programme
    # year, but all units from the previous year must be passed
    # before entering the next programme year.
    # ==========================================================

    validate_year_boundary_progression(
        enrollment,
        next_level,
    )

    # ==========================================================
    # 8. DETERMINE NEXT ACADEMIC PERIOD
    # ==========================================================

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

    # ==========================================================
    # 9. PREVENT DUPLICATE ENROLLMENT
    # ==========================================================

    if SemesterEnrollment.objects.filter(
        student=enrollment.student,
        academic_year=next_year,
        semester=next_semester,
    ).exists():

        raise ValueError(
            "Student is already enrolled in the next semester."
        )

    # ==========================================================
    # 10. CREATE NEXT SEMESTER ENROLLMENT
    # ==========================================================

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

    # ==========================================================
    # 11. CLOSE CURRENT ENROLLMENT
    # ==========================================================

    enrollment.status = (
        SemesterEnrollment.PROGRESSED
    )

    enrollment.save()

    # ==========================================================
    # 12. AUDIT LOG
    # ==========================================================

    ProgressionLog.objects.create(
        student=enrollment.student,
        from_enrollment=enrollment,
        to_enrollment=new_enrollment,
        action=ProgressionLog.PROMOTED,
        performed_by=user,
    )

    return new_enrollment