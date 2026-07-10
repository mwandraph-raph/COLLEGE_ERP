from django.shortcuts import render, redirect
from .models import (Student,
                     Programme,
                     Department, 
                     AcademicYear, 
                     Semester, 
                     Course, 
                     Unit,
                     Registration,
                     StudyLevel,
                     SemesterEnrollment,
                     Applicant,
                     Intake,
                     )
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .utils import generate_admission_no
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from .forms import (
    DepartmentForm,
    ProgrammeForm,
    StudentForm,
    AcademicYearForm,
    SemesterForm,
    CourseForm,
    UnitForm,
    RegistrationForm,
    StudyLevelForm,
    SemesterEnrollmentForm,
    ApplicantForm,
    IntakeForm,
)

# Create your views here.
@login_required
def home(request):

    context = {}

    active_year = AcademicYear.objects.filter(
        is_active=True
    ).first()

    active_semester = Semester.objects.filter(
        is_active=True
    ).first()

    context["active_year"] = active_year
    context["active_semester"] = active_semester

    # Student Dashboard
    if hasattr(request.user, "student_profile"):

        student = request.user.student_profile

        enrollment = SemesterEnrollment.objects.filter(
            student=student
        ).order_by("-id").first()

        registration_count = 0

        if enrollment:
            registration_count = Registration.objects.filter(
                enrollment=enrollment
            ).count()

        context.update({
            "dashboard_type": "student",
            "student": student,
            "enrollment": enrollment,
            "registration_count": registration_count,
        })

    # Administrator Dashboard
    elif request.user.is_superuser:

        context.update({
            "dashboard_type": "admin",
            "total_students": Student.objects.count(),
            "total_programmes": Programme.objects.count(),
            "total_departments": Department.objects.count(),
            "total_applicants": Applicant.objects.count(),
            "total_enrollments": SemesterEnrollment.objects.count(),
            "total_registrations": Registration.objects.count(),
            "total_users": User.objects.count(),
        })

# Registrar Dashboard
    elif request.user.has_perm("students.view_registration"):

        context.update({
            "dashboard_type": "registrar",
            "total_students": Student.objects.count(),
            "total_enrollments": SemesterEnrollment.objects.count(),
            "total_registrations": Registration.objects.count(),
        })

    # Admissions Dashboard
    elif request.user.has_perm("students.view_applicant"):

        context.update({
            "dashboard_type": "admissions",
            "total_applicants": Applicant.objects.count(),
            "pending_applicants": Applicant.objects.filter(
                status="PENDING"
            ).count(),
            "approved_applicants": Applicant.objects.filter(
                status="APPROVED"
            ).count(),
            "rejected_applicants": Applicant.objects.filter(
                status="REJECTED"
            ).count(),
            "total_intakes": Intake.objects.count(),
        })

    else:

        context["dashboard_type"] = "general"

    return render(
        request,
        "students/home.html",
        context,
    )

@login_required
@permission_required(
    "students.view_student",
    raise_exception=True,
)
def student_list(request):

    query = request.GET.get("q")

    students = (

        Student.objects

        .select_related(

            "programme",

            "programme__department",

            "study_level"

        )

    )

    if query:

        students = students.filter(

            Q(admission_no__icontains=query) |

            Q(first_name__icontains=query) |

            Q(last_name__icontains=query)

        )

    paginator = Paginator(
        students,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    return render(

        request,

        "students/student_list.html",

        {

            "page_obj": page_obj,

            "query": query,

            "total_students": students.count(),

        },

    )

@login_required
@permission_required(
    "students.add_student",
    raise_exception=True,
)
def student_create(request):
    """
    Register a new student.
    """
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                  request,
                     "Student created successfully."
                     )
            return redirect("student_list")
    else:
        form = StudentForm()
    context = {
        "form": form,
    }

    return render(
        request,
        "students/student_form.html",
        context,
    )

@login_required
@permission_required(
    "students.view_student",
    raise_exception=True,
)

@login_required
@permission_required(
    "students.view_student",
    raise_exception=True
)
def student_detail(request, id):
    """
    Display details for a single student
    including semester enrollment history.
    """

    student = get_object_or_404(
        Student,
        id=id,
    )


    enrollments = (
        student.enrollments
        .select_related(
            "academic_year",
            "semester",
            "study_level",
        )
        .all()
    )


    context = {

        "student": student,

        "enrollments": enrollments,

    }


    return render(
        request,
        "students/student_detail.html",
        context,
    )

@login_required
@permission_required(
    "students.change_student",
    raise_exception=True,
)
def student_update(request, id):
    """
    Update an existing student.
    """
    student = get_object_or_404(
        Student,
        id=id,
    )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            instance=student,
        )
        if form.is_valid():

            form.save()
            messages.success(
                  request,
                     "Student updated successfully."
                     )
            return redirect(
                "student_detail",
                id=student.id,
            )

    else:
        form = StudentForm(
            instance=student,
        )

    context = {
        "form": form,
        "student": student,
    }

    return render(
        request,
        "students/student_form.html",
        context,
    )

@login_required
@permission_required(
    "students.delete_student",
    raise_exception=True,
)
def student_delete(request, id):
    """
    Delete an existing student.
    """

    student = get_object_or_404(
        Student,
        id=id,
    )

    if request.method == "POST":

        student.delete()

        return redirect(
            "student_list"
        )

    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        },
    )


@login_required
@permission_required(
    "students.view_department",
    raise_exception=True
)
def department_list(request):

    departments = Department.objects.all()

    context = {
        "departments": departments
    }

    return render(
        request,
        "students/departments/department_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_department",
    raise_exception=True
)
def department_create(request):

    if request.method == "POST":

        form = DepartmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Department created successfully."
            )

            return redirect("department_list")

    else:

        form = DepartmentForm()

    context = {
        "form": form
    }

    return render(
        request,
        "students/departments/department_form.html",
        context
    )

@login_required
@permission_required(
    "students.change_department",
    raise_exception=True
)
def department_update(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            instance=department
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Department updated successfully."
            )

            return redirect("department_list")

    else:

        form = DepartmentForm(
            instance=department
        )

    context = {
        "form": form,
        "department": department
    }

    return render(
        request,
        "students/departments/department_form.html",
        context
    )

@login_required
@permission_required(
    "students.delete_department",
    raise_exception=True
)
def department_delete(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == "POST":

        department.delete()

        messages.success(
            request,
            "Department deleted successfully."
        )

        return redirect("department_list")

    context = {
        "department": department
    }

    return render(
        request,
        "students/departments/department_confirm_delete.html",
        context
    )

@login_required
@permission_required(
    "students.view_programme",
    raise_exception=True
)
def programme_list(request):

    programmes = Programme.objects.select_related(
        "department"
    )

    context = {
        "programmes": programmes
    }

    return render(
        request,
        "students/programmes/programme_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_programme",
    raise_exception=True
)
def programme_create(request):

    if request.method == "POST":

        form = ProgrammeForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Programme created successfully."
            )

            return redirect(
                "programme_list"
            )

    else:

        form = ProgrammeForm()

    return render(
        request,
        "students/programmes/programme_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_programme",
    raise_exception=True
)
def programme_update(request, pk):

    programme = get_object_or_404(
        Programme,
        pk=pk
    )

    if request.method == "POST":

        form = ProgrammeForm(
            request.POST,
            instance=programme
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Programme updated successfully."
            )

            return redirect(
                "programme_list"
            )

    else:

        form = ProgrammeForm(
            instance=programme
        )

    return render(
        request,
        "students/programmes/programme_form.html",
        {
            "form": form,
            "programme": programme
        }
    )

@login_required
@permission_required(
    "students.delete_programme",
    raise_exception=True
)
def programme_delete(request, pk):

    programme = get_object_or_404(
        Programme,
        pk=pk
    )

    if request.method == "POST":

        programme.delete()

        messages.success(
            request,
            "Programme deleted successfully."
        )

        return redirect(
            "programme_list"
        )

    return render(
        request,
        "students/programmes/programme_confirm_delete.html",
        {
            "programme": programme
        }
    )

@login_required
@permission_required(
    "students.view_academicyear",
    raise_exception=True
)
def academic_year_list(request):

    years = AcademicYear.objects.all()

    return render(
        request,
        "students/academic_years/academic_year_list.html",
        {
            "years": years
        }
    )

@login_required
@permission_required(
    "students.add_academicyear",
    raise_exception=True
)
def academic_year_create(request):

    if request.method == "POST":

        form = AcademicYearForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Academic year created successfully."
            )

            return redirect(
                "academic_year_list"
            )

    else:

        form = AcademicYearForm()

    return render(
        request,
        "students/academic_years/academic_year_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_academicyear",
    raise_exception=True
)
def academic_year_update(request, pk):

    year = get_object_or_404(
        AcademicYear,
        pk=pk
    )

    if request.method == "POST":

        form = AcademicYearForm(
            request.POST,
            instance=year
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Academic year updated successfully."
            )

            return redirect(
                "academic_year_list"
            )

    else:

        form = AcademicYearForm(
            instance=year
        )

    return render(
        request,
        "students/academic_years/academic_year_form.html",
        {
            "form": form
        }
    )


@login_required
@permission_required(
    "students.delete_academicyear",
    raise_exception=True
)
def academic_year_delete(request, pk):

    year = get_object_or_404(
        AcademicYear,
        pk=pk
    )

    if request.method == "POST":

        year.delete()

        messages.success(
            request,
            "Academic year deleted successfully."
        )

        return redirect(
            "academic_year_list"
        )

    return render(
        request,
        "students/academic_years/academic_year_confirm_delete.html",
        {
            "year": year
        }
    )


@login_required
@permission_required(
    "students.change_academicyear",
    raise_exception=True
)
def open_registration(request, pk):

    year = get_object_or_404(
        AcademicYear,
        pk=pk
    )

    year.registration_open = True

    year.save()

    messages.success(
        request,
        f"Registration opened for {year.year_name}"
    )

    return redirect(
        "academic_year_list"
    )


@login_required
@permission_required(
    "students.change_academicyear",
    raise_exception=True
)
def close_registration(request, pk):

    year = get_object_or_404(
        AcademicYear,
        pk=pk
    )

    year.registration_open = False

    year.save()

    messages.success(
        request,
        f"Registration closed for {year.year_name}"
    )

    return redirect(
        "academic_year_list"
    )

@login_required
@permission_required(
    "students.view_semester",
    raise_exception=True
)
def semester_list(request):

    semesters = Semester.objects.select_related(
        "academic_year"
    )

    return render(
        request,
        "students/semesters/semester_list.html",
        {
            "semesters": semesters
        }
    )


@login_required
@permission_required(
    "students.add_semester",
    raise_exception=True
)
def semester_create(request):

    if request.method == "POST":

        form = SemesterForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Semester created successfully."
            )

            return redirect(
                "semester_list"
            )

    else:

        form = SemesterForm()

    return render(
        request,
        "students/semesters/semester_form.html",
        {
            "form": form,
            "title": "Create Semester"
        }
    )


@login_required
@permission_required(
    "students.change_semester",
    raise_exception=True
)
def semester_update(request, pk):

    semester = get_object_or_404(
        Semester,
        pk=pk
    )

    if request.method == "POST":

        form = SemesterForm(
            request.POST,
            instance=semester
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Semester updated successfully."
            )

            return redirect(
                "semester_list"
            )

    else:

        form = SemesterForm(
            instance=semester
        )

    return render(
        request,
        "students/semesters/semester_form.html",
        {
            "form": form,
            "title": "Edit Semester"
        }
    )


@login_required
@permission_required(
    "students.delete_semester",
    raise_exception=True
)
def semester_delete(request, pk):

    semester = get_object_or_404(
        Semester,
        pk=pk
    )

    if request.method == "POST":

        semester.delete()

        messages.success(
            request,
            "Semester deleted successfully."
        )

        return redirect(
            "semester_list"
        )

    return render(
        request,
        "students/semesters/semester_confirm_delete.html",
        {
            "semester": semester
        }
    )

@login_required
@permission_required(
    "students.change_semester",
    raise_exception=True
)
def activate_semester(request, pk):

    semester = get_object_or_404(
        Semester,
        pk=pk
    )

    academic_year = (
        semester.academic_year
    )

    academic_year.is_active = True
    academic_year.save()

    semester.is_active = True
    semester.save()

    messages.success(
        request,
        (
            f"{semester.semester_name} "
            f"activated for "
            f"{academic_year.year_name}"
        )
    )

    return redirect(
        "semester_list"
    )

@login_required
@permission_required(
    "students.view_course",
    raise_exception=True
)
def course_list(request):

    courses = (
        Course.objects
        .select_related(
            "programme",
            "study_level",
            "semester",
            "programme__department"
        )
    )

    search = request.GET.get(
        "search"
    )

    programme_id = request.GET.get(
        "programme"
    )

    semester_id = request.GET.get(
        "semester"
    )

    level_id = request.GET.get(
        "study_level"
    )

    if search:

        courses = courses.filter(
            course_name__icontains=search
        )

    if programme_id:

        courses = courses.filter(
            programme_id=programme_id
        )

    if level_id:

        courses = courses.filter(
            study_level_id=level_id
        )

    if semester_id:

        courses = courses.filter(
            semester_id=semester_id
        )

    context = {

        "courses": courses,

        "programmes":
            Programme.objects.all(),

        "study_levels":
            StudyLevel.objects.all(),

        "semesters":
            Semester.objects.all(),

        "search": search,

        "selected_programme":
            programme_id,

        "selected_level":
            level_id,

        "selected_semester":
            semester_id,
    }

    return render(
        request,
        "students/courses/course_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_course",
    raise_exception=True
)
def course_create(request):

    if request.method == "POST":

        form = CourseForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course created successfully."
            )

            return redirect(
                "course_list"
            )

    else:

        form = CourseForm()

    return render(
        request,
        "students/courses/course_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_course",
    raise_exception=True
)
def course_update(request, pk):

    course = get_object_or_404(
        Course,
        pk=pk
    )

    if request.method == "POST":

        form = CourseForm(
            request.POST,
            instance=course
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course updated successfully."
            )

            return redirect(
                "course_list"
            )

    else:

        form = CourseForm(
            instance=course
        )

    return render(
        request,
        "students/courses/course_form.html",
        {
            "form": form,
            "course": course
        }
    )

@login_required
@permission_required(
    "students.delete_course",
    raise_exception=True
)
def course_delete(request, pk):

    course = get_object_or_404(
        Course,
        pk=pk
    )

    if request.method == "POST":

        course.delete()

        messages.success(
            request,
            "Course deleted successfully."
        )

        return redirect(
            "course_list"
        )

    return render(
        request,
        "students/courses/course_confirm_delete.html",
        {
            "course": course
        }
    )

@login_required
@permission_required(
    "students.view_unit",
    raise_exception=True
)
def unit_list(request):

    units = (
        Unit.objects
        .select_related(
            "course",
            "course__programme"
        )
    )

    search = request.GET.get(
        "search"
    )

    course_id = request.GET.get(
        "course"
    )

    if search:

        units = units.filter(
            unit_name__icontains=search
        )

    if course_id:

        units = units.filter(
            course_id=course_id
        )

    context = {

        "units": units,

        "courses":
            Course.objects.all(),

        "search": search,

        "selected_course":
            course_id,
    }

    return render(
        request,
        "students/units/unit_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_unit",
    raise_exception=True
)
def unit_create(request):

    if request.method == "POST":

        form = UnitForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Unit created successfully."
            )

            return redirect(
                "unit_list"
            )

    else:

        form = UnitForm()

    return render(
        request,
        "students/units/unit_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_unit",
    raise_exception=True
)
def unit_update(request, pk):

    unit = get_object_or_404(
        Unit,
        pk=pk
    )

    if request.method == "POST":

        form = UnitForm(
            request.POST,
            instance=unit
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Unit updated successfully."
            )

            return redirect(
                "unit_list"
            )

    else:

        form = UnitForm(
            instance=unit
        )

    return render(
        request,
        "students/units/unit_form.html",
        {
            "form": form,
            "unit": unit
        }
    )

@login_required
@permission_required(
    "students.delete_unit",
    raise_exception=True
)
def unit_delete(request, pk):

    unit = get_object_or_404(
        Unit,
        pk=pk
    )

    if request.method == "POST":

        unit.delete()

        messages.success(
            request,
            "Unit deleted successfully."
        )

        return redirect(
            "unit_list"
        )

    return render(
        request,
        "students/units/unit_confirm_delete.html",
        {
            "unit": unit
        }
    )

@login_required
@permission_required(
    "students.view_registration",
    raise_exception=True
)
def registration_list(request):

    registrations = (

        Registration.objects

        .select_related(

            "enrollment",

            "enrollment__student",

            "enrollment__academic_year",

            "enrollment__semester",

            "unit"

        )

    )

    search = request.GET.get(
        "search"
    )

    year_id = request.GET.get(
        "academic_year"
    )

    semester_id = request.GET.get(
        "semester"
    )

    if search:

        registrations = registrations.filter(

            enrollment__student__admission_no__icontains=search

        )

    if year_id:

        registrations = registrations.filter(

            enrollment__academic_year_id=year_id

        )

    if semester_id:

        registrations = registrations.filter(

            enrollment__semester_id=semester_id

        )

    academic_years = AcademicYear.objects.all()

    semesters = Semester.objects.select_related(
        "academic_year"
    )

    context = {

        "registrations": registrations,

        "academic_years": academic_years,

        "semesters": semesters,

        "search": search,

        "selected_year": year_id,

        "selected_semester": semester_id,

    }

    return render(

        request,

        "students/registrations/registration_list.html",

        context

    )

@login_required
@permission_required(
    "students.add_registration",
    raise_exception=True
)
def registration_create(request):

    if request.method == "POST":

        form = RegistrationForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Registration created successfully."
            )

            return redirect(
                "registration_list"
            )

    else:

        form = RegistrationForm()

    return render(
        request,
        "students/registrations/registration_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_registration",
    raise_exception=True
)
def registration_update(request, pk):

    registration = get_object_or_404(
        Registration,
        pk=pk
    )

    if request.method == "POST":

        form = RegistrationForm(
            request.POST,
            instance=registration
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Registration updated successfully."
            )

            return redirect(
                "registration_list"
            )

    else:

        form = RegistrationForm(
            instance=registration
        )

    return render(
        request,
        "students/registrations/registration_form.html",
        {
            "form": form,
            "registration": registration
        }
    )

@login_required
@permission_required(
    "students.delete_registration",
    raise_exception=True
)
def registration_delete(request, pk):

    registration = get_object_or_404(
        Registration,
        pk=pk
    )

    if request.method == "POST":

        registration.delete()

        messages.success(
            request,
            "Registration deleted successfully."
        )

        return redirect(
            "registration_list"
        )

    return render(
        request,
        "students/registrations/registration_confirm_delete.html",
        {
            "registration": registration
        }
    )

@login_required
def my_registrations(request):

    student = get_object_or_404(

        Student,

        user=request.user

    )

    registrations = (

        Registration.objects

        .filter(

            enrollment__student=student

        )

        .select_related(

            "enrollment",

            "enrollment__academic_year",

            "enrollment__semester",

            "unit"

        )

        .order_by(

            "-registration_date"

        )

    )

    return render(

        request,

        "students/registrations/my_registrations.html",

        {

            "student": student,

            "registrations": registrations

        }

    )

@login_required
def register_units(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    enrollment = SemesterEnrollment.objects.filter(
        student=student,
        status="enrolled"
    ).select_related(
        "academic_year",
        "semester",
        "study_level"
    ).first()

    if not enrollment:

        messages.error(
            request,
            (
                "You are not enrolled in any "
                "semester. Contact administration."
            )
        )

        return redirect(
            "my_registrations"
        )

    if not enrollment.academic_year.registration_open:

        messages.error(
            request,
            "Unit registration is currently closed."
        )

        return redirect(
            "my_registrations"
        )

    units = (

        Unit.objects

        .filter(

            course__programme=student.programme,

            course__study_level=enrollment.study_level,

            course__semester=enrollment.semester

        )

        .select_related(

            "course",

            "course__study_level",

            "course__semester"

        )

        .order_by(

            "unit_code"

        )

    )

    if request.method == "POST":

        unit_ids = request.POST.getlist(
            "units"
        )

        count = 0

        for unit_id in unit_ids:

            unit = get_object_or_404(

                Unit,

                pk=unit_id,

                course__programme=student.programme,

                course__study_level=enrollment.study_level,

                course__semester=enrollment.semester

            )

            registration, created = (

                Registration.objects.get_or_create(

                    enrollment=enrollment,

                    unit=unit

                )

            )

            if created:

                count += 1

        messages.success(
            request,
            f"{count} unit(s) registered successfully."
        )

        return redirect(
            "my_registrations"
        )

    context = {

        "student": student,

        "enrollment": enrollment,

        "units": units,

    }

    return render(

        request,

        "students/registrations/register_units.html",

        context

    )

@login_required
def drop_registration(request, pk):

    student = get_object_or_404(
        Student,
        user=request.user
    )

    registration = get_object_or_404(
        Registration,
        pk=pk,
        enrollment__student=student
    )

    if not registration.enrollment.academic_year.registration_open:

        messages.error(
            request,
            "Registration changes are closed."
        )

        return redirect(
            "my_registrations"
        )

    if request.method == "POST":

        registration.delete()

        messages.success(
            request,
            "Unit dropped successfully."
        )

        return redirect(
            "my_registrations"
        )

    return render(
        request,
        "students/registrations/drop_registration.html",
        {
            "registration": registration
        }
    )

@login_required
@permission_required(
    "students.view_studylevel",
    raise_exception=True
)
def study_level_list(request):

    levels = StudyLevel.objects.all()

    return render(
        request,
        "students/study_levels/study_level_list.html",
        {
            "levels": levels
        }
    )

@login_required
@permission_required(
    "students.add_studylevel",
    raise_exception=True
)
def study_level_create(request):

    form = StudyLevelForm(
        request.POST or None
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Study Level created successfully."
        )

        return redirect(
            "study_level_list"
        )

    return render(
        request,
        "students/study_levels/study_level_form.html",
        {
            "form": form,
            "title": "Add Study Level"
        }
    )

@login_required
@permission_required(
    "students.change_studylevel",
    raise_exception=True
)
def study_level_update(request, pk):

    level = get_object_or_404(
        StudyLevel,
        pk=pk
    )

    form = StudyLevelForm(
        request.POST or None,
        instance=level
    )

    if form.is_valid():

        form.save()

        messages.success(
            request,
            "Study Level updated successfully."
        )

        return redirect(
            "study_level_list"
        )

    return render(
        request,
        "students/study_levels/study_level_form.html",
        {
            "form": form,
            "title": "Edit Study Level"
        }
    )

@login_required
@permission_required(
    "students.delete_studylevel",
    raise_exception=True
)
def study_level_delete(request, pk):

    level = get_object_or_404(
        StudyLevel,
        pk=pk
    )

    if request.method == "POST":

        level.delete()

        messages.success(
            request,
            "Study Level deleted successfully."
        )

        return redirect(
            "study_level_list"
        )

    return render(
        request,
        "students/study_levels/study_level_confirm_delete.html",
        {
            "level": level
        }
    )

@login_required
@permission_required(
    "students.view_semesterenrollment",
    raise_exception=True
)
def enrollment_list(request):

    enrollments = SemesterEnrollment.objects.select_related(
        "student",
        "academic_year",
        "semester",
        "study_level"
    )

    # Search
    search = request.GET.get("search")

    if search:

        enrollments = enrollments.filter(
            Q(
                student__admission_no__icontains=search
            )
            |
            Q(
                student__first_name__icontains=search
            )
            |
            Q(
                student__last_name__icontains=search
            )
        )


    # Filters

    academic_year = request.GET.get(
        "academic_year"
    )

    if academic_year:

        enrollments = enrollments.filter(
            academic_year_id=academic_year
        )


    semester = request.GET.get(
        "semester"
    )

    if semester:

        enrollments = enrollments.filter(
            semester_id=semester
        )


    study_level = request.GET.get(
        "study_level"
    )

    if study_level:

        enrollments = enrollments.filter(
            study_level_id=study_level
        )


    status = request.GET.get(
        "status"
    )

    if status:

        enrollments = enrollments.filter(
            status=status
        )


    context = {

        "enrollments": enrollments,

        "academic_years":
            AcademicYear.objects.all(),

        "semesters":
            Semester.objects.all(),

        "study_levels":
            StudyLevel.objects.all(),

    }

    return render(
        request,
        "students/enrollments/enrollment_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_semesterenrollment",
    raise_exception=True
)
def enrollment_create(request):

    active_year = AcademicYear.objects.get(
        is_active=True
    )

    active_semester = Semester.objects.get(
        is_active=True
    )


    if request.method == "POST":

        form = SemesterEnrollmentForm(
            request.POST
        )


        if form.is_valid():

            enrollment = form.save(
                commit=False
            )


            # Check duplicate enrollment

            exists = SemesterEnrollment.objects.filter(
                student=enrollment.student,
                academic_year=active_year,
                semester=active_semester
            ).exists()


            if exists:

                messages.error(
                    request,
                    "This student is already enrolled in the current semester."
                )

                return redirect(
                    "enrollment_create"
                )


            # Assign academic details

            enrollment.academic_year = active_year

            enrollment.semester = active_semester

            enrollment.study_level = (
                enrollment.student.study_level
            )


            enrollment.save()


            messages.success(
                request,
                "Student enrolled successfully."
            )


            return redirect(
                "enrollment_list"
            )


    else:

        form = SemesterEnrollmentForm()


    return render(
        request,
        "students/enrollments/enrollment_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.view_semesterenrollment",
    raise_exception=True
)
def enrollment_detail(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )

    return render(
        request,
        "students/enrollments/enrollment_detail.html",
        {
            "enrollment": enrollment
        }
    )

@login_required
@permission_required(
    "students.change_semesterenrollment",
    raise_exception=True
)
def enrollment_update(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )

    if request.method == "POST":

        form = SemesterEnrollmentForm(
            request.POST,
            instance=enrollment
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Enrollment updated successfully."
            )

            return redirect(
                "enrollment_list"
            )

    else:

        form = SemesterEnrollmentForm(
            instance=enrollment
        )

    return render(
        request,
        "students/enrollments/enrollment_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.delete_semesterenrollment",
    raise_exception=True
)
def enrollment_delete(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )

    if request.method == "POST":

        enrollment.delete()

        messages.success(
            request,
            "Enrollment deleted successfully."
        )

        return redirect(
            "enrollment_list"
        )

    return render(
        request,
        "students/enrollments/enrollment_confirm_delete.html",
        {
            "enrollment": enrollment
        }
    )

@login_required
@permission_required(
    "students.view_applicant",
    raise_exception=True
)
def applicant_list(request):

    applicants = Applicant.objects.all()

    return render(
        request,
        "students/applicants/applicant_list.html",
        {
            "applicants": applicants
        }
    )

@login_required
@permission_required(
    "students.add_applicant",
    raise_exception=True
)
def applicant_create(request):

    if request.method == "POST":

        form = ApplicantForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Applicant created."
            )

            return redirect(
                "applicant_list"
            )

    else:

        form = ApplicantForm()

    return render(
        request,
        "students/applicants/applicant_form.html",
        {
            "form": form
        }
    )

@login_required
@permission_required(
    "students.change_applicant",
    raise_exception=True
)
def applicant_update(
    request,
    pk
):

    applicant = get_object_or_404(
        Applicant,
        pk=pk
    )

    if request.method == "POST":

        form = ApplicantForm(
            request.POST,
            instance=applicant
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Applicant updated."
            )

            return redirect(
                "applicant_list"
            )

    else:

        form = ApplicantForm(
            instance=applicant
        )

    return render(
        request,
        "students/applicants/applicant_form.html",
        {
            "form": form
        }
    )


@login_required
@permission_required(
    "students.delete_applicant",
    raise_exception=True
)
def applicant_delete(
    request,
    pk
):

    applicant = get_object_or_404(
        Applicant,
        pk=pk
    )

    if request.method == "POST":

        applicant.delete()

        messages.success(
            request,
            "Applicant deleted."
        )

        return redirect(
            "applicant_list"
        )

    return render(
        request,
        "students/applicants/applicant_confirm_delete.html",
        {
            "applicant": applicant
        }
    )

@login_required
@permission_required(
    "students.change_applicant",
    raise_exception=True
)
def approve_applicant(request, pk):

    applicant = get_object_or_404(
        Applicant,
        pk=pk
    )

    if applicant.student:

        messages.warning(
            request,
            "Applicant has already been approved."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )

    study_level = (
        StudyLevel.objects
        .order_by("id")
        .first()
    )

    if not study_level:

        messages.error(
            request,
            "No study level has been configured."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )

    active_year = (
        AcademicYear.objects
        .filter(is_active=True)
        .first()
    )

    active_semester = (
        Semester.objects
        .filter(is_active=True)
        .first()
    )

    if not active_year:

        messages.error(
            request,
            "No active academic year found."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )

    if not active_semester:

        messages.error(
            request,
            "No active semester found."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )

    try:

        with transaction.atomic():

            student = Student.objects.create(

                first_name=applicant.first_name,

                last_name=applicant.last_name,

                phone=applicant.phone_number,

                programme=applicant.programme,

                study_level=study_level,
            )

            applicant.student = student

            applicant.status = "APPROVED"

            applicant.save()

            SemesterEnrollment.objects.create(

                student=student,

                academic_year=active_year,

                semester=active_semester,

                study_level=study_level,

                status="enrolled"
            )

        messages.success(

            request,

            (
                f"Applicant approved successfully. "
                f"Student {student.admission_no} created."
            )
        )

    except Exception as e:

        messages.error(
            request,
            f"Approval failed: {e}"
        )

    return redirect(
        "applicant_detail",
        pk=applicant.pk
    )

@login_required
@permission_required(
    "students.view_applicant",
    raise_exception=True
)
def applicant_detail(request, pk):

    applicant = get_object_or_404(
        Applicant,
        pk=pk
    )

    return render(
        request,
        "students/applicants/applicant_detail.html",
        {
            "applicant": applicant
        }
    )


@login_required
@permission_required(
    "students.view_intake",
    raise_exception=True
)
def intake_list(request):

    intakes = Intake.objects.all()

    return render(
        request,
        "students/intakes/intake_list.html",
        {
            "intakes": intakes
        }
    )

@login_required
@permission_required(
    "students.add_intake",
    raise_exception=True
)
def intake_create(request):

    if request.method == "POST":

        form = IntakeForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Intake created successfully."
            )

            return redirect(
                "intake_list"
            )

    else:

        form = IntakeForm()


    return render(
        request,
        "students/intakes/intake_form.html",
        {
            "form": form,
            "title": "Add Intake"
        }
    )

@login_required
@permission_required(
    "students.change_intake",
    raise_exception=True
)
def intake_update(request, pk):

    intake = get_object_or_404(
        Intake,
        pk=pk
    )


    if request.method == "POST":

        form = IntakeForm(
            request.POST,
            instance=intake
        )


        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Intake updated successfully."
            )

            return redirect(
                "intake_list"
            )

    else:

        form = IntakeForm(
            instance=intake
        )


    return render(
        request,
        "students/intakes/intake_form.html",
        {
            "form": form,
            "title": "Edit Intake"
        }
    )


@login_required
@permission_required(
    "students.delete_intake",
    raise_exception=True
)
def intake_delete(request, pk):

    intake = get_object_or_404(
        Intake,
        pk=pk
    )


    if request.method == "POST":

        intake.delete()

        messages.success(
            request,
            "Intake deleted successfully."
        )

        return redirect(
            "intake_list"
        )


    return render(
        request,
        "students/intakes/intake_confirm_delete.html",
        {
            "intake": intake
        }
    )


