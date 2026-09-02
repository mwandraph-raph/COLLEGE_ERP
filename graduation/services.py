from students.models import (
    SemesterEnrollment,
    Registration,
    Result,
    Unit,
    ProgrammeLevel,
)

from finance.models import FinancialClearance
from students.services import sync_final_academic_completion

# ==========================================================
# ENROLLMENT HELPERS
# ==========================================================

def get_student_enrollments(student):
    """
    Return every semester enrollment for a student.

    Historical enrollments are preserved and are never replaced
    merely because the student progresses to another semester.
    """

    return (
        SemesterEnrollment.objects
        .filter(
            student=student,
        )
        .select_related(
            "academic_year",
            "semester",
            "programme_level",
            "programme",
        )
        .order_by(
            "programme_level__progression_order",
            "academic_year__id",
            "semester__id",
            "id",
        )
    )


def get_completed_study_levels(student):
    """
    Return programme levels reached by the student.

    This is used for curriculum discovery.

    Reaching a level through progression does NOT mean
    that level has been completed.
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
    Return all curriculum units belonging to programme levels
    reached by the student.

    Every required unit must eventually have a PASS result.
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
            "programme_level__progression_order",
            "code",
        )
    )


# ==========================================================
# REGISTRATION UNIT HELPER
# ==========================================================

def get_registration_unit_id(registration):
    """
    Determine the actual Unit represented by a registration.
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
# SEMESTER COMPLETION HELPER
# ==========================================================

def semester_completion_status(enrollment):
    """
    Determine whether a specific semester enrollment has
    actually been completed.

    A semester is completed only when:

    1. It has registered units.
    2. Every registered unit has a result.
    3. Every result is PASS.

    IMPORTANT:

    An enrollment being created, ENROLLED, or PROGRESSED does
    not by itself mean that the semester is completed.

    Progression into another semester therefore cannot
    automatically complete that semester.
    """

    registrations = list(
        Registration.objects
        .filter(
            enrollment=enrollment,
        )
        .select_related(
            "unit",
            "unit_offering",
            "unit_offering__unit",
            "result",
        )
    )

    if not registrations:
        return {
            "completed": False,
            "issues": [
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "has no registered units."
            ],
        }

    issues = []

    for registration in registrations:

        result = getattr(
            registration,
            "result",
            None,
        )

        unit = (
            registration.unit
            or (
                registration.unit_offering.unit
                if (
                    registration.unit_offering_id
                    and registration.unit_offering
                )
                else None
            )
        )

        unit_name = str(
            unit or "registered unit"
        )

        if not result:

            issues.append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester}: "
                f"No result found for {unit_name}."
            )

            continue

        if result.remarks != "PASS":

            issues.append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester}: "
                f"{unit_name} has not been passed."
            )

    return {
        "completed": not issues,
        "issues": issues,
    }


# ==========================================================
# ACADEMIC ASSESSMENT
# ==========================================================

def academic_assessment(student):
    """
    Academic graduation assessment.

    Graduation academic requirements are satisfied only when:

    • Student has semester enrollments.
    • Curriculum units exist.
    • Every curriculum unit has been registered.
    • Every registered curriculum unit has a result.
    • The result belongs to a PUBLISHED ResultBatch.
    • The published result is PASS.

    IMPORTANT:
    An APPROVED result is NOT enough for graduation.
    Results must be PUBLISHED before they count as final academic
    results for graduation.
    """

    from students.models import ResultBatch

    summary = {
        "required_units": 0,
        "passed_units": 0,
        "failed_units": 0,
        "missing_results": 0,
        "missing_units": 0,
        "status": False,
        "issues": [],
    }

    # ======================================================
    # 1. STUDENT ENROLLMENTS
    # ======================================================

    enrollments = get_student_enrollments(student)

    if not enrollments.exists():

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    # ======================================================
    # 2. REQUIRED CURRICULUM UNITS
    # ======================================================

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

    # ======================================================
    # 3. STUDENT REGISTRATIONS
    # ======================================================

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
            "result__batch",
        )
    )

    if not registrations:

        summary["issues"].append(
            "Student has not registered any units."
        )

        return summary

    # ======================================================
    # 4. MAP ACTUAL UNIT IDS TO REGISTRATIONS
    # ======================================================

    registration_map = {}

    for registration in registrations:

        unit_id = get_registration_unit_id(
            registration
        )

        if not unit_id:
            continue

        registration_map.setdefault(
            unit_id,
            []
        ).append(
            registration
        )

    # ======================================================
    # 5. CHECK EVERY CURRICULUM UNIT
    # ======================================================

    for unit in required_units:

        unit_registrations = registration_map.get(
            unit.id,
            []
        )

        # --------------------------------------------------
        # NEVER REGISTERED
        # --------------------------------------------------

        if not unit_registrations:

            summary["missing_units"] += 1

            summary["issues"].append(
                f"{unit} has never been registered."
            )

            continue

        # --------------------------------------------------
        # LOOK FOR A PUBLISHED PASS
        # --------------------------------------------------

        published_pass = False
        published_fail = False
        approved_not_published = False
        has_any_result = False

        for registration in unit_registrations:

            result = getattr(
                registration,
                "result",
                None,
            )

            if not result:
                continue

            has_any_result = True

            batch = getattr(
                result,
                "batch",
                None,
            )

            # ==============================================
            # RESULT NOT YET PUBLISHED
            # ==============================================

            if not batch or batch.status != ResultBatch.PUBLISHED:

                approved_not_published = True

                continue

            # ==============================================
            # PUBLISHED PASS
            # ==============================================

            if result.remarks == "PASS":

                published_pass = True
                break

            # ==============================================
            # PUBLISHED FAIL
            # ==============================================

            if result.remarks == "FAIL":

                published_fail = True

        # --------------------------------------------------
        # PUBLISHED PASS FOUND
        # --------------------------------------------------

        if published_pass:

            summary["passed_units"] += 1

            continue

        # --------------------------------------------------
        # PUBLISHED FAILURE
        # --------------------------------------------------

        if published_fail:

            summary["failed_units"] += 1

            summary["issues"].append(
                f"Failed {unit}."
            )

            continue

        # --------------------------------------------------
        # RESULT EXISTS BUT NOT PUBLISHED
        # --------------------------------------------------

        if approved_not_published:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"Result for {unit} has been entered/approved "
                "but has not yet been published."
            )

            continue

        # --------------------------------------------------
        # RESULT EXISTS BUT NO PASS
        # --------------------------------------------------

        if has_any_result:

            summary["missing_results"] += 1

            summary["issues"].append(
                f"Published result for {unit} is not passed."
            )

            continue

        # --------------------------------------------------
        # NO RESULT
        # --------------------------------------------------

        summary["missing_results"] += 1

        summary["issues"].append(
            f"No result found for {unit}."
        )

    # ======================================================
    # 6. FINAL ACADEMIC DECISION
    # ======================================================

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
    Graduation financial assessment.

    EVERY semester enrollment must be financially cleared.

    A student cannot graduate while ANY semester has an
    outstanding graduation financial clearance.
    """

    summary = {
        "status": False,
        "issues": [],
    }

    enrollments = list(
        get_student_enrollments(student)
    )

    if not enrollments:

        summary["issues"].append(
            "Student has no semester enrollments."
        )

        return summary

    all_cleared = True

    for enrollment in enrollments:

        try:

            clearance = enrollment.financial_clearance

        except FinancialClearance.DoesNotExist:

            all_cleared = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "has no financial clearance record."
            )

            continue

        if not clearance.graduation_cleared:

            all_cleared = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "graduation financial clearance pending."
            )

    summary["status"] = all_cleared

    return summary


# ==========================================================
# PROGRESSION / SEMESTER COMPLETION ASSESSMENT
# ==========================================================

# ==========================================================
# PROGRESSION / SEMESTER COMPLETION ASSESSMENT
# ==========================================================

def progression_assessment(student):
    """
    Determine programme completion from actual academic records.

    A semester is considered completed only when:

    • It has registrations.
    • Every registered unit has a result.
    • Every result belongs to a PUBLISHED ResultBatch.
    • Every published result is PASS.

    APPROVED results do NOT count as final completion.
    Results must be PUBLISHED.

    The student must also have completed the FINAL
    ProgrammeLevel configured for their programme.

    The final ProgrammeLevel is determined dynamically using
    progression_order.
    """

    from students.models import ProgrammeLevel, ResultBatch

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
                "result__batch",
                "enrollment__programme_level",
            )
        )

        # ======================================================
        # NO REGISTRATIONS
        # ======================================================

        if not registrations:

            all_completed = False

            summary["issues"].append(
                f"{enrollment.academic_year} - "
                f"{enrollment.semester} "
                "has no registered units."
            )

            continue

        semester_completed = True

        # ======================================================
        # CHECK EVERY REGISTRATION
        # ======================================================

        for registration in registrations:

            result = getattr(
                registration,
                "result",
                None,
            )

            # --------------------------------------------------
            # DETERMINE REGISTERED UNIT
            # --------------------------------------------------

            unit = (
                registration.unit
                or (
                    registration.unit_offering.unit
                    if (
                        registration.unit_offering_id
                        and registration.unit_offering
                    )
                    else None
                )
            )

            # ==================================================
            # MISSING RESULT
            # ==================================================

            if not result:

                semester_completed = False
                all_completed = False

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"No result found for "
                    f"{unit or 'registered unit'}."
                )

                continue

            # ==================================================
            # RESULT HAS NO BATCH
            # ==================================================

            if not result.batch:

                semester_completed = False
                all_completed = False

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"{unit or 'registered unit'} "
                    "has a result that is not attached "
                    "to a result batch."
                )

                continue

            # ==================================================
            # RESULT NOT PUBLISHED
            # ==================================================

            if result.batch.status != ResultBatch.PUBLISHED:

                semester_completed = False
                all_completed = False

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"{unit or 'registered unit'} "
                    "result has not yet been published."
                )

                continue

            # ==================================================
            # PUBLISHED RESULT BUT NOT PASSED
            # ==================================================

            if result.remarks != "PASS":

                semester_completed = False
                all_completed = False

                summary["issues"].append(
                    f"{enrollment.academic_year} - "
                    f"{enrollment.semester}: "
                    f"{unit or 'registered unit'} "
                    "has not been passed."
                )

                continue

        # ======================================================
        # SEMESTER COMPLETED
        # ======================================================

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

    # ==========================================================
    # NO PROGRAMME LEVELS CONFIGURED
    # ==========================================================

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

    # ==========================================================
    # STUDENT HAS NOT COMPLETED ANY LEVEL
    # ==========================================================

    if not highest_completed_level:

        all_completed = False

        summary["issues"].append(
            "Student has not completed any programme level. "
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
            "Programme completion is outstanding. "
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
    Central production graduation eligibility engine.

    Graduation requires ALL THREE:

        1. Academic completion
        2. Financial clearance
        3. Programme / semester completion

    Before assessment begins, the system synchronizes the
    student's final academic enrollment to COMPLETED when
    the final semester has genuinely been completed.

    IMPORTANT:

    COMPLETED and APPROVED are separate workflow states.

    COMPLETED
        = Academic programme completion.

    APPROVED
        = Graduation approval.
    """

    # ------------------------------------------------------
    # SYNCHRONIZE FINAL ACADEMIC COMPLETION
    # ------------------------------------------------------
    #
    # This does NOT approve graduation.
    #
    # It only ensures that when the student's final academic
    # requirements are genuinely complete, the final
    # SemesterEnrollment is marked COMPLETED.
    #
    sync_final_academic_completion(
        student
    )

    # ------------------------------------------------------
    # ACADEMIC ASSESSMENT
    # ------------------------------------------------------

    academic = academic_assessment(
        student
    )

    # ------------------------------------------------------
    # FINANCIAL ASSESSMENT
    # ------------------------------------------------------

    finance = finance_assessment(
        student
    )

    # ------------------------------------------------------
    # PROGRESSION / SEMESTER COMPLETION
    # ------------------------------------------------------

    progression = progression_assessment(
        student
    )

    # ------------------------------------------------------
    # FINAL ELIGIBILITY
    # ------------------------------------------------------

    eligible = (
        academic["status"]
        and finance["status"]
        and progression["status"]
    )

    # ------------------------------------------------------
    # COLLECT ALL ISSUES
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------

    classification = {
        "average": None,
        "classification": None,
        "results_count": 0,
    }

    if eligible:

        classification = graduation_classification(
            student
        )

    # ------------------------------------------------------
    # FINAL ASSESSMENT RESPONSE
    # ------------------------------------------------------

    return {
        "eligible": eligible,
        "academic": academic,
        "finance": finance,
        "progression": progression,
        "classification": classification,
        "issues": issues,
    }

# ==========================================================
# OVERALL GRADUATION CLASSIFICATION
# ==========================================================

def graduation_classification(student):
    """
    Calculate the student's overall graduation classification.

    Results are taken from ALL published results across the
    student's semester enrollments.

    Classification:

        70 - 100  = DISTINCTION
        60 - 69   = CREDIT
        50 - 59   = PASS
        Below 50  = FAIL

    A classification is returned only when the student's
    academic graduation requirements have been satisfied.
    """

    from students.models import ResultBatch

    enrollments = list(
        get_student_enrollments(student)
    )

    if not enrollments:
        return {
            "average": None,
            "classification": None,
            "results_count": 0,
        }

    registrations = (
        Registration.objects
        .filter(
            enrollment__in=enrollments
        )
        .select_related(
            "result",
            "result__batch",
        )
    )

    marks = []

    for registration in registrations:

        result = getattr(
            registration,
            "result",
            None,
        )

        if not result:
            continue

        if not result.batch:
            continue

        if result.batch.status != ResultBatch.PUBLISHED:
            continue

        # --------------------------------------------------
        # CALCULATE RESULT MARK
        # --------------------------------------------------

        cat1 = result.cat1 or 0
        cat2 = result.cat2 or 0
        exam = result.exam or 0

        total = (
            cat1
            + cat2
            + exam
        )

        marks.append(
            float(total)
        )

    if not marks:

        return {
            "average": None,
            "classification": None,
            "results_count": 0,
        }

    overall_average = (
        sum(marks) / len(marks)
    )

    if overall_average >= 70:
        classification = "DISTINCTION"

    elif overall_average >= 60:
        classification = "CREDIT"

    elif overall_average >= 50:
        classification = "PASS"

    else:
        classification = "FAIL"

    return {
        "average": round(
            overall_average,
            2,
        ),
        "classification": classification,
        "results_count": len(marks),
    }



# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def graduation_eligibility(student):
    """
    Backward-compatible wrapper.

    Existing code can continue using:

        graduation_eligibility(student)
    """

    return graduation_assessment(
        student
    )

