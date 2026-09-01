from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
)
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.utils import timezone

from students.models import (
    Student,
    Programme,
    ProgrammeLevel,
)

from .models import Graduation
from .services import graduation_assessment


# ==========================================================
# GRADUATION ELIGIBILITY LIST
# ==========================================================

@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def eligibility_list(request):

    programmes = (
        Programme.objects
        .select_related("course")
        .order_by("name")
    )

    programme_id = request.GET.get("programme")

    students_queryset = (
        Student.objects
        .select_related("programme")
        .prefetch_related(
            "enrollments__academic_year",
            "enrollments__semester",
            "enrollments__programme_level",
        )
        .order_by("admission_no")
    )

    candidates = []

    for student in students_queryset:

        # --------------------------------------------------
        # FIND FINAL PROGRAMME LEVEL
        # --------------------------------------------------

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

        if not final_level:
            continue

        # --------------------------------------------------
        # FIND STUDENT'S HIGHEST ENROLLMENT
        # --------------------------------------------------

        latest_enrollment = (
            student.enrollments
            .select_related(
                "academic_year",
                "semester",
                "programme_level",
            )
            .order_by(
                "-programme_level__progression_order",
                "-academic_year__id",
                "-semester__id",
                "-id",
            )
            .first()
        )

        if not latest_enrollment:
            continue

        # --------------------------------------------------
        # ONLY FINAL-LEVEL STUDENTS ENTER THE
        # GRADUATION ELIGIBILITY WORKFLOW
        # --------------------------------------------------

        if (
            latest_enrollment.programme_level_id
            != final_level.id
        ):
            continue

        # --------------------------------------------------
        # RUN THE ASSESSMENT
        #
        # This does NOT determine whether the student
        # appears on the candidate list.
        #
        # It determines whether they are actually eligible.
        # --------------------------------------------------

        assessment = graduation_assessment(
            student
        )

        # --------------------------------------------------
        # EXISTING GRADUATION RECORD
        # --------------------------------------------------

        existing_graduation = (
            Graduation.objects
            .filter(
                student=student,
            )
            .order_by("-id")
            .first()
        )

        candidates.append(
            {
                "student": student,
                "latest_enrollment": latest_enrollment,
                "final_level": final_level,
                "assessment": assessment,
                "existing_graduation": existing_graduation,
            }
        )

    # ======================================================
    # PROGRAMME FILTER
    # ======================================================

    if programme_id:

        try:

            programme_id = int(
                programme_id
            )

            candidates = [
                candidate
                for candidate in candidates
                if candidate["student"].programme_id
                == programme_id
            ]

        except (
            TypeError,
            ValueError,
        ):

            programme_id = None

    # ======================================================
    # CONTEXT
    # ======================================================

    context = {
        "candidates": candidates,
        "programmes": programmes,
        "selected_programme": programme_id,
    }

    return render(
        request,
        "graduation/eligibility_list.html",
        context,
    )


# ==========================================================
# CHECK GRADUATION ELIGIBILITY
# ==========================================================

@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def graduation_eligibility_view(
    request,
    student_id,
):

    student = get_object_or_404(
        Student,
        pk=student_id,
    )

    # ------------------------------------------------------
    # RUN REAL GRADUATION ASSESSMENT
    # ------------------------------------------------------

    assessment = graduation_assessment(
        student
    )

    # ------------------------------------------------------
    # EXISTING GRADUATION RECORD
    # ------------------------------------------------------

    existing_graduation = (
        Graduation.objects
        .filter(
            student=student,
        )
        .order_by("-id")
        .first()
    )

    # ------------------------------------------------------
    # FINAL PROGRAMME LEVEL
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # CURRENT / HIGHEST ENROLLMENT
    # ------------------------------------------------------

    latest_enrollment = (
        student.enrollments
        .select_related(
            "academic_year",
            "semester",
            "programme_level",
        )
        .order_by(
            "-programme_level__progression_order",
            "-academic_year__id",
            "-semester__id",
            "-id",
        )
        .first()
    )

    context = {
        "student": student,
        "assessment": assessment,
        "report": assessment,
        "existing_graduation": existing_graduation,
        "final_level": final_level,
        "latest_enrollment": latest_enrollment,
    }

    return render(
        request,
        "graduation/eligibility.html",
        context,
    )


# ==========================================================
# APPROVE GRADUATION
# ==========================================================

@login_required
@permission_required(
    "graduation.change_graduation",
    raise_exception=True,
)
def approve_graduation(
    request,
    student_id,
):

    if request.method != "POST":

        return redirect(
            "graduation:graduation_eligibility",
            student_id=student_id,
        )

    student = get_object_or_404(
        Student,
        pk=student_id,
    )

    # ======================================================
    # ALWAYS RE-CHECK ELIGIBILITY
    # ======================================================

    assessment = graduation_assessment(
        student
    )

    if not assessment["eligible"]:

        messages.error(
            request,
            (
                "Student cannot be approved for graduation "
                "because all graduation requirements have "
                "not been satisfied."
            ),
        )

        return redirect(
            "graduation:graduation_eligibility",
            student_id=student.id,
        )

    # ======================================================
    # GET FINAL / CURRENT ENROLLMENT
    # ======================================================

    latest_enrollment = (
        student.enrollments
        .select_related(
            "academic_year",
            "semester",
            "programme_level",
        )
        .order_by(
            "-programme_level__progression_order",
            "-academic_year__id",
            "-semester__id",
            "-id",
        )
        .first()
    )

    if not latest_enrollment:

        messages.error(
            request,
            "Student has no semester enrollment.",
        )

        return redirect(
            "graduation:graduation_eligibility",
            student_id=student.id,
        )

    # ======================================================
    # FIND EXISTING GRADUATION RECORD
    #
    # IMPORTANT:
    # Graduation.student is UNIQUE.
    #
    # Therefore we MUST search by student only.
    # We must NOT use academic_year in get_or_create().
    # ======================================================

    graduation = (
        Graduation.objects
        .filter(
            student=student,
        )
        .first()
    )

    # ======================================================
    # CREATE ONLY IF NO RECORD EXISTS
    # ======================================================

    if graduation is None:

        graduation = Graduation.objects.create(
            student=student,
            academic_year=latest_enrollment.academic_year,
            status="APPROVED",
            approved_by=request.user,
            approved_date=timezone.now(),
            remarks=(
                "Student has satisfied graduation "
                "eligibility requirements."
            ),
        )

    # ======================================================
    # EXISTING RECORD
    #
    # NEVER CREATE A SECOND RECORD.
    # UPDATE THE EXISTING RECORD.
    # ======================================================

    else:

        graduation.status = "APPROVED"
        graduation.academic_year = (
            latest_enrollment.academic_year
        )
        graduation.approved_by = request.user
        graduation.approved_date = timezone.now()

        graduation.remarks = (
            "Student has satisfied graduation "
            "eligibility requirements."
        )

        graduation.save(
            update_fields=[
                "status",
                "academic_year",
                "approved_by",
                "approved_date",
                "remarks",
                "updated_at",
            ]
        )

    # ======================================================
    # SUCCESS
    # ======================================================

    messages.success(
        request,
        (
            f"{student.admission_no} has been approved "
            "for graduation."
        ),
    )

    return redirect(
        "graduation:graduation_list",
    )


# ==========================================================
# APPROVED GRADUATION LIST
# ==========================================================

@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def graduation_list(request):

    graduations = (
        Graduation.objects
        .filter(
            status="APPROVED"
        )
        .select_related(
            "student",
            "student__programme",
            "academic_year",
            "approved_by",
        )
        .order_by(
            "-approved_date",
            "student__admission_no",
        )
    )

    context = {
        "graduations": graduations,
    }

    return render(
        request,
        "graduation/graduation_list.html",
        context,
    )