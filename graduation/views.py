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

from students.models import Student, Programme

from .models import Graduation
from .services import graduation_assessment


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
        # USE THE SAME GRADUATION ASSESSMENT ENGINE
        # --------------------------------------------------

        assessment = graduation_assessment(
            student
        )

        # --------------------------------------------------
        # ONLY SHOW ACTUALLY ELIGIBLE STUDENTS
        # --------------------------------------------------

        if assessment["eligible"]:

            latest_enrollment = (
                student.enrollments
                .select_related(
                    "academic_year",
                    "semester",
                    "programme_level",
                )
                .order_by(
                    "-academic_year__id",
                    "-semester__id",
                )
                .first()
            )

            if latest_enrollment:

                candidates.append(
                    {
                        "student": student,
                        "latest_enrollment": latest_enrollment,
                        "assessment": assessment,
                    }
                )

    # ------------------------------------------------------
    # PROGRAMME FILTER
    # ------------------------------------------------------

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



@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def graduation_eligibility_view(request, student_id):

    student = get_object_or_404(
        Student,
        pk=student_id,
    )

    assessment = graduation_assessment(student)

    existing_graduation = (
        Graduation.objects
        .filter(student=student)
        .order_by("-id")
        .first()
    )

    context = {
        "student": student,
        "assessment": assessment,
        "report": assessment,
        "existing_graduation": existing_graduation,
    }

    return render(
        request,
        "graduation/eligibility.html",
        context,
    )


@login_required
@permission_required(
    "graduation.change_graduation",
    raise_exception=True,
)
def approve_graduation(request, student_id):

    if request.method != "POST":
        return redirect(
            "graduation:graduation_eligibility",
            student_id=student_id,
        )

    student = get_object_or_404(
        Student,
        pk=student_id,
    )

    assessment = graduation_assessment(student)

    if not assessment["eligible"]:
        messages.error(
            request,
            "Student cannot be approved for graduation because "
            "all graduation requirements have not been satisfied.",
        )

        return redirect(
            "graduation:graduation_eligibility",
            student_id=student.id,
        )

    latest_enrollment = (
        student.enrollments
        .select_related("academic_year")
        .order_by(
            "-academic_year__id",
            "-semester__id",
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

    graduation, created = Graduation.objects.get_or_create(
        student=student,
        academic_year=latest_enrollment.academic_year,
        defaults={
            "status": "ELIGIBLE",
            "remarks": "Student has satisfied graduation eligibility requirements.",
        },
    )

    if graduation.status != "APPROVED":

        graduation.status = "APPROVED"
        graduation.approved_by = request.user
        graduation.approved_date = timezone.now()

        graduation.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_date",
                "updated_at",
            ]
        )

    messages.success(
        request,
        f"{student.admission_no} has been approved for graduation.",
    )

    return redirect(
        "graduation:graduation_list",
    )


@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def graduation_list(request):

    graduations = (
        Graduation.objects
        .filter(status="APPROVED")
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