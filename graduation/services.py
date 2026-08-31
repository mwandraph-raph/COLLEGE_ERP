from students.models import (
    SemesterEnrollment,
    Registration,
    Result,
    Unit,
)

from finance.models import FinancialClearance


# ==========================================================
# ENROLLMENT HELPERS
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
            "programme_level",
            "programme",
        )
        .order_by(
            "academic_year__id",
            "semester__id",
        )
    )


def get_completed_study_levels(student):
    """
    Return all programme levels reached by the student.
    """

    return (
        get_student_enrollments(student)
        .values_list(
            "programme_level_id",
            flat=True,
        )
        .distinct()
    )


def get_required_units(student):
    """
    Return all curriculum units belonging to the
    student's programme levels.
    """

    programme_levels = get_completed_study_levels(student)

    return (
        Unit.objects
        .filter(
            programme_level_id__in=programme_levels,
        )
        .select_related(
            "programme_level",
        )
        .distinct()
        .order_by(
            "programme_level_id",
            "code",
        )
    )


# ==========================================================
# REGISTRATION UNIT HELPER
# ==========================================================

def get_registration_unit_id(registration):
    """
    Determine the actual Unit represented by a registration.

    Some registrations may have the Unit directly through
    registration.unit, while others are linked through
    registration.unit_offering.unit.

    This prevents graduation from incorrectly reporting
    registered units as missing.
    """

    if registration.unit_id:
        return registration.unit_id

    if (
        registration.unit_offering_id
        and registration.unit_offering
        and registration.unit_offering.unit_id
    ):
        return registration.unit_offering.unit_id

    return None


# ==========================================================
# ACADEMIC ASSESSMENT
# ==========================================================

def academic_assessment(student):
    """
    Academic graduation assessment.

    Rules:

    • Student must have semester enrollments.
    • Curriculum units must exist.
    • Every curriculum unit must be registered.
    • Every registered curriculum unit must have a result.
    • Every curriculum unit must be passed.

    Registration matching uses both:

        Registration.unit
        Registration.unit_offering.unit

    so the assessment agrees with the actual academic records.
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

    if not enrollments.exists():

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    # ------------------------------------------------------
    # CURRICULUM
    # ------------------------------------------------------

    required_units = list(
        get_required_units(student)
    )

    if not required_units:

        summary["issues"].append(
            "No curriculum has been configured "
            "for the student's programme."
        )

        return summary

    summary["required_units"] = len(
        required_units
    )

    # ------------------------------------------------------
    # ALL STUDENT REGISTRATIONS
    # ------------------------------------------------------

    registrations = list(
        Registration.objects
        .filter(
            enrollment__in=enrollments
        )
        .select_related(
            "enrollment",
            "unit",
            "unit_offering",
            "unit_offering__unit",
            "result",
        )
    )

    if not registrations:

        summary["issues"].append(
            "Student has not registered any units."
        )

        return summary

    # ------------------------------------------------------
    # MAP ACTUAL UNIT IDS TO REGISTRATIONS
    # ------------------------------------------------------

    registration_map = {}

    for registration in registrations:

        unit_id = get_registration_unit_id(
            registration
        )

        if not unit_id:
            continue

        # Keep the first valid registration.
        # If the student repeated a unit, the later
        # passed result should also be considered below.
        registration_map.setdefault(
            unit_id,
            []
        ).append(
            registration
        )

    # ------------------------------------------------------
    # CHECK EVERY CURRICULUM UNIT
    # ------------------------------------------------------

    for unit in required_units:

        unit_registrations = registration_map.get(
            unit.id,
            []
        )

        if not unit_registrations:

            summary["missing_units"] += 1

            summary["issues"].append(
                f"{unit} has never been registered."
            )

            continue

        # --------------------------------------------------
        # FIND A PASSED RESULT FIRST
        # --------------------------------------------------

        passed_registration = None

        for registration in unit_registrations:

            result = getattr(
                registration,
                "result",
                None,
            )

            if result and result.remarks == "PASS":

                passed_registration = registration
                break

        if passed_registration:

            summary["passed_units"] += 1

            continue

        # --------------------------------------------------
        # NO PASSED RESULT
        # --------------------------------------------------

        has_result = False
        has_failed_result = False

        for registration in unit_registrations:

            result = getattr(
                registration,
                "result",
                None,
            )

            if not result:
                continue

            has_result = True

            if result.remarks == "FAIL":
                has_failed_result = True

        if has_failed_result:

            summary["failed_units"] += 1

            summary["issues"].append(
                f"Failed {unit}."
            )

        elif has_result:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"Result for {unit} is not yet passed."
            )

        else:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"No result found for {unit}."
            )

    # ------------------------------------------------------
    # FINAL ACADEMIC DECISION
    # ------------------------------------------------------

    summary["status"] = (
        summary["required_units"] > 0
        and summary["passed_units"]
        == summary["required_units"]
        and summary["failed_units"] == 0
        and summary["missing_results"] == 0
        and summary["missing_units"] == 0
    )

    return summary


# ==========================================================
# FINANCIAL ASSESSMENT
# ==========================================================

def finance_assessment(student):
    """
    Check financial graduation clearance.

    Every semester enrollment must have a
    Financial Clearance record and graduation_cleared
    must be True.
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
# PROGRESSION / SEMESTER COMPLETION ASSESSMENT
# ==========================================================

def progression_assessment(student):
    """
    Determine programme completion from actual academic records.

    A semester is considered completed when:

    • It has registrations.
    • Every registered unit has a result.
    • Every result is PASS.

    In addition, a student must have completed the FINAL
    ProgrammeLevel configured for their programme before they
    can satisfy the programme-completion requirement.

    The final ProgrammeLevel is determined by the highest
    progression_order.
    """

    summary = {
        "status": False,
        "issues": [],
    }

    # ==========================================================
    # 1. GET ALL STUDENT ENROLLMENTS
    # ==========================================================

    enrollments = list(
        get_student_enrollments(student)
    )

    if not enrollments:

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    all_completed = True

    completed_levels = []

    # ==========================================================
    # 2. CHECK EACH ENROLLED SEMESTER
    # ==========================================================

    for enrollment in enrollments:

        registrations = list(
            Registration.objects
            .filter(
                enrollment=enrollment
            )
            .select_related(
                "unit",
                "unit_offering",
                "unit_offering__unit",
                "result",
                "enrollment__programme_level",
            )
        )

        # ------------------------------------------------------
        # No registrations
        # ------------------------------------------------------

        if not registrations:

            all_completed = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "has no registered units."
            )

            continue

        semester_completed = True

        # ------------------------------------------------------
        # Check every registration
        # ------------------------------------------------------

        for registration in registrations:

            result = getattr(
                registration,
                "result",
                None,
            )

            # --------------------------------------------------
            # Missing result
            # --------------------------------------------------

            if not result:

                semester_completed = False

                unit = (
                    registration.unit
                    or (
                        registration.unit_offering.unit
                        if registration.unit_offering_id
                        and registration.unit_offering
                        else None
                    )
                )

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"No result found for "
                    f"{unit or 'registered unit'}."
                )

                continue

            # --------------------------------------------------
            # Failed / not passed
            # --------------------------------------------------

            if result.remarks != "PASS":

                semester_completed = False

                unit = (
                    registration.unit
                    or (
                        registration.unit_offering.unit
                        if registration.unit_offering_id
                        and registration.unit_offering
                        else None
                    )
                )

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"{unit or 'registered unit'} "
                    "has not been passed."
                )

        # ------------------------------------------------------
        # Semester completed
        # ------------------------------------------------------

        if semester_completed:

            if enrollment.programme_level_id:

                completed_levels.append(
                    enrollment.programme_level
                )

        else:

            all_completed = False

    # ==========================================================
    # 3. FIND FINAL PROGRAMME LEVEL
    # ==========================================================
    #
    # ProgrammeLevel has:
    #
    #     programme
    #     year
    #     semester
    #     progression_order
    #
    # Therefore we can determine the final level dynamically.
    # No year or semester is hard-coded.
    #

    from students.models import ProgrammeLevel

    final_level = (
        ProgrammeLevel.objects
        .filter(
            programme=student.programme,
            is_active=True,
        )
        .order_by(
            "-progression_order"
        )
        .first()
    )

    # ----------------------------------------------------------
    # No programme levels configured
    # ----------------------------------------------------------

    if not final_level:

        all_completed = False

        summary["issues"].append(
            "No programme levels have been configured "
            "for the student's programme."
        )

        summary["status"] = False

        return summary

    # ==========================================================
    # 4. FIND HIGHEST COMPLETED PROGRAMME LEVEL
    # ==========================================================

    highest_completed_level = None

    if completed_levels:

        highest_completed_level = max(
            completed_levels,
            key=lambda level: level.progression_order,
        )

    # ----------------------------------------------------------
    # Student has not completed any level
    # ----------------------------------------------------------

    if not highest_completed_level:

        all_completed = False

        summary["issues"].append(
            f"Student has not completed any programme level. "
            f"Final programme level is "
            f"{final_level.name}."
        )

        summary["status"] = False

        return summary

    # ==========================================================
    # 5. CHECK FINAL PROGRAMME LEVEL
    # ==========================================================

    if (
        highest_completed_level.progression_order
        < final_level.progression_order
    ):

        all_completed = False

        summary["issues"].append(
            f"Programme completion is outstanding. "
            f"Student has completed "
            f"{highest_completed_level.name}, "
            f"but the final programme level is "
            f"{final_level.name}."
        )

    # ==========================================================
    # 6. FINAL PROGRESSION STATUS
    # ==========================================================

    summary["status"] = all_completed

    return summary



# ==========================================================
# MASTER GRADUATION ASSESSMENT
# ==========================================================

def graduation_assessment(student):
    """
    Production Graduation Eligibility Engine.

    This is the central function used by:

    • Graduation
    • Transcript
    • Certificate
    • Alumni
    • Graduation Approval
    """

    academic = academic_assessment(
        student
    )

    finance = finance_assessment(
        student
    )

    progression = progression_assessment(
        student
    )

    eligible = (
        academic["status"]
        and finance["status"]
        and progression["status"]
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
# BACKWARD COMPATIBILITY
# ==========================================================

def graduation_eligibility(student):
    """
    Backward compatibility wrapper.

    Older views can continue calling:

        graduation_eligibility(student)
    """

    return graduation_assessment(
        student
    )
