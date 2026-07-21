from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from students.models import Student
from .services import graduation_assessment
from students.models import Student


from students.models import Student, Programme


@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def eligibility_list(request):

    programmes = (
        Programme.objects
        .select_related("department")
        .order_by("programme_name")
    )


    programme_id = request.GET.get("programme")


    students_queryset = (
        Student.objects
        .select_related(
            "programme"
        )
        .prefetch_related(
            "enrollments__academic_year",
            "enrollments__semester",
            "enrollments__study_level",
        )
        .order_by("admission_no")
    )


    candidates = []


    for student in students_queryset:


        latest_enrollment = (
            student.enrollments
            .order_by(
                "-academic_year__id",
                "-semester__id"
            )
            .first()
        )


        if latest_enrollment:


            if latest_enrollment.status == "completed":


                candidates.append(
                    {
                        "student": student,
                        "latest_enrollment": latest_enrollment,
                    }
                )



    # Programme filter

    if programme_id:


        candidates = [

            candidate

            for candidate in candidates

            if candidate["student"].programme_id == int(programme_id)

        ]



    context = {


        "candidates": candidates,


        "programmes": programmes,


        "selected_programme": programme_id,


    }


    return render(

        request,

        "graduation/eligibility_list.html",

        context

    )


@login_required
@permission_required(
    "graduation.view_graduation",
    raise_exception=True,
)
def graduation_eligibility(request, student_id):


    student = get_object_or_404(
        Student,
        id=student_id
    )


    latest_enrollment = (
        student.enrollments
        .order_by(
            "-academic_year__id",
            "-semester__id"
        )
        .first()
    )


    context = {

        "student": student,

        "latest_enrollment": latest_enrollment,

    }


    return render(

        request,

        "graduation/graduation_eligibility.html",

        context

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

    context = {
        "student": student,
        "assessment": assessment,
        "report": assessment,   # Temporary backward compatibility
    }

    return render(
        request,
        "graduation/eligibility.html",
        context,
    )