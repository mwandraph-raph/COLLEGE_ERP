from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import (
                    Font,
                    Alignment,
                    Border,
                    Side
                )
from .models import (Student,
                     Programme,
                     Department, 
                     AcademicYear, 
                     Semester, 
                     Course, 
                     Unit,
                     Registration,
                     SemesterEnrollment,
                     Applicant,
                     Intake,
                     LecturerAssignment,
                     Result,
                     ResultBatch,
                     ResultBatchLog,
                     ProgrammeLevel,
                     )
from finance.models import (
    FeeStructure,
    StudentInvoice,
    InvoiceItem,
    FinancialClearance,
)
from finance.services import (
    generate_student_invoice,
    update_financial_clearance,
)
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .utils import generate_admission_no
from django.db import transaction
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)

from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .forms import (
    DepartmentForm,
    ProgrammeForm,
    StudentForm,
    AcademicYearForm,
    SemesterForm,
    CourseForm,
    UnitForm,
    RegistrationForm,
    SemesterEnrollmentForm,
    ApplicantForm,
    IntakeForm,
    LecturerAssignmentForm,
    ProgrammeLevelForm,
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

    # Lecturer Dashboard
    elif request.user.groups.filter(
        name="Lecturer"
    ).exists():

        context.update({

            "dashboard_type": "lecturer",

            "my_units":
                LecturerAssignment.objects.filter(
                    lecturer=request.user,
                    academic_year__is_active=True,
                    semester__is_active=True,
                ).values(
                    "unit"
                ).distinct().count(),

            "my_students":
                Registration.objects.filter(
                    enrollment__academic_year__is_active=True,
                    enrollment__semester__is_active=True,
                    unit__lecturer_assignments__lecturer=request.user,
                ).distinct().count(),
        })

    # Exam Officer Dashboard
    elif request.user.has_perm(
        "students.view_lecturerassignment"
    ):

        context.update({

            "dashboard_type": "exam",

            "total_assignments":
                LecturerAssignment.objects.count(),

            "assigned_units":
                LecturerAssignment.objects.values(
                    "unit"
                ).distinct().count(),

            "total_registrations":
                Registration.objects.count(),

            "pending_approvals":
                Result.objects.filter(
                    is_submitted=True,
                    is_approved=False
                ).values(
                    "unit"
                ).distinct().count(),
        })

    # Registrar Dashboard
    elif request.user.has_perm(
        "students.view_registration"
    ):

        context.update({
            "dashboard_type": "registrar",
            "total_students": Student.objects.count(),
            "total_enrollments": SemesterEnrollment.objects.count(),
            "total_registrations": Registration.objects.count(),
        })

    # Admissions Dashboard
    elif request.user.has_perm(
        "students.view_applicant"
    ):

        context.update({
            "dashboard_type": "admissions",

            "total_applicants":
                Applicant.objects.count(),

            "pending_applicants":
                Applicant.objects.filter(
                    status="PENDING"
                ).count(),

            "approved_applicants":
                Applicant.objects.filter(
                    status="APPROVED"
                ).count(),

            "rejected_applicants":
                Applicant.objects.filter(
                    status="REJECTED"
                ).count(),

            "total_intakes":
                Intake.objects.count(),
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
            "programme__course",
            "programme__course__department",
        )
        .order_by(
            "admission_no"
        )
    )


    if query:

        students = students.filter(
            Q(admission_no__icontains=query)
            |
            Q(first_name__icontains=query)
            |
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
        }
    )

@login_required
@permission_required(
    "students.add_student",
    raise_exception=True,
)
def student_create(request):

    if request.method == "POST":

        form = StudentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Student created successfully."
            )

            return redirect(
                "student_list"
            )

    else:

        form = StudentForm()


    return render(
        request,
        "students/student_form.html",
        {
            "form": form
        }
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

    student = get_object_or_404(
        Student,
        id=id
    )


    enrollments = (
        student.enrollments
        .select_related(
            "academic_year",
            "semester",
            "programme",
            "programme_level",
        )
        .order_by(
            "-academic_year",
            "-semester"
        )
    )


    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "enrollments": enrollments,
        }
    )

@login_required
@permission_required(
    "students.change_student",
    raise_exception=True,
)
def student_update(request, id):

    student = get_object_or_404(
        Student,
        id=id
    )


    if request.method == "POST":

        form = StudentForm(
            request.POST,
            instance=student
        )


        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Student updated successfully."
            )

            return redirect(
                "student_detail",
                id=student.id
            )

    else:

        form = StudentForm(
            instance=student
        )


    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "student": student,
        }
    )

@login_required
@permission_required(
    "students.delete_student",
    raise_exception=True,
)
def student_delete(request,id):

    student = get_object_or_404(
        Student,
        id=id
    )


    if request.method == "POST":

        student.delete()

        messages.success(
            request,
            "Student deleted successfully."
        )

        return redirect(
            "student_list"
        )


    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student":student
        }
    )


@login_required
@permission_required(
    "students.view_department",
    raise_exception=True
)
def department_list(request):

    departments = (
        Department.objects
        .all()
        .order_by(
            "name"
        )
    )


    return render(
        request,
        "students/departments/department_list.html",
        {
            "departments": departments
        }
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

    programmes = (
        Programme.objects
        .select_related(
            "course",
            "course__department",
        )
        .order_by(
            "name"
        )
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
            "department"
        )
        .order_by(
            "name"
        )
    )


    search = request.GET.get(
        "search"
    )


    department_id = request.GET.get(
        "department"
    )


    if search:

        courses = courses.filter(
            name__icontains=search
        )


    if department_id:

        courses = courses.filter(
            department_id=department_id
        )


    context = {

        "courses": courses,

        "departments": (
            Department.objects
            .order_by(
                "name"
            )
        ),

        "search": search,

        "selected_department": department_id,

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
            "programme_level",
            "programme_level__programme",
            "programme_level__programme__course",
        )
        .order_by(
            "programme_level__programme__name",
            "programme_level__progression_order",
            "code",
        )
    )


    search = request.GET.get(
        "search"
    )


    programme_level_id = request.GET.get(
        "programme_level"
    )


    if search:

        units = units.filter(
            name__icontains=search
        )


    if programme_level_id:

        units = units.filter(
            programme_level_id=programme_level_id
        )


    context = {

        "units": units,


        "programme_levels": (
            ProgrammeLevel.objects
            .select_related(
                "programme",
            )
            .filter(
                is_active=True
            )
            .order_by(
                "programme__name",
                "progression_order",
            )
        ),


        "search": search,


        "selected_programme_level":
            programme_level_id,
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
            "enrollment__programme",
            "enrollment__programme_level",
            "enrollment__academic_year",
            "enrollment__semester",
            "unit",
        )
        .order_by(
            "-enrollment__academic_year",
            "-enrollment__semester",
            "unit__code",
        )
    )


    search = request.GET.get(
        "search"
    )


    if search:

        registrations = registrations.filter(
            Q(
                enrollment__student__admission_no__icontains=search
            )
            |
            Q(
                enrollment__student__first_name__icontains=search
            )
            |
            Q(
                unit__code__icontains=search
            )
        )


    context = {

        "registrations": registrations,

        "search": search,

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

            registration = form.save()

            messages.success(
                request,
                "Unit registered successfully."
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
            "registration": registration,
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
            "enrollment__programme",
            "enrollment__programme_level",
            "unit",
            "unit__programme_level",
        )
        .order_by(
            "-enrollment__academic_year",
            "-enrollment__semester",
            "unit__code"
        )
    )


    return render(
        request,
        "students/registrations/my_registrations.html",
        {
            "student": student,
            "registrations": registrations,
        }
    )


@login_required
def register_units(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment.objects.select_related(
            "student",
            "programme_level",
            "academic_year",
            "semester",
        ),
        pk=pk,
    )

    available_units = (
        enrollment.programme_level.units
        .filter(is_active=True)
        .order_by("code")
    )

    # Student must be enrolled
    if enrollment.status != SemesterEnrollment.ENROLLED:

        messages.error(
            request,
            "Only enrolled students can register units."
        )

        return redirect(
            "semester_enrollment_detail",
            pk=enrollment.pk,
        )

    # Registration window must be open
    if not enrollment.academic_year.registration_open:

        messages.error(
            request,
            "Unit registration is currently closed."
        )

        return redirect(
            "semester_enrollment_detail",
            pk=enrollment.pk,
        )

    # -----------------------------
    # Financial eligibility check
    # -----------------------------
    clearance = getattr(
        enrollment,
        "financial_clearance",
        None,
    )

    if not clearance:

        messages.error(
            request,
            "Financial clearance has not been processed for this semester."
        )

        return redirect(
            "semester_enrollment_detail",
            pk=enrollment.pk,
        )

    if not clearance.registration_cleared:

        messages.error(
            request,
            "You have not met the financial requirements for unit registration."
        )

        return redirect(
            "semester_enrollment_detail",
            pk=enrollment.pk,
        )

    if request.method == "POST":

        unit_ids = request.POST.getlist("units")

        # Nothing selected
        if not unit_ids:

            messages.error(
                request,
                "Please select at least one unit before registering."
            )

            return redirect(
                "register_units",
                pk=enrollment.pk,
            )

        registered = 0
        duplicates = 0

        with transaction.atomic():

            selected_units = available_units.filter(
                id__in=unit_ids
            )

            for unit in selected_units:

                _, created = Registration.objects.get_or_create(
                    enrollment=enrollment,
                    unit=unit,
                    defaults={
                        "registration_type": Registration.NORMAL,
                    },
                )

                if created:

                    registered += 1

                else:

                    duplicates += 1

        if registered:

            if duplicates:

                messages.success(
                    request,
                    f"{registered} unit(s) registered successfully. "
                    f"{duplicates} were already registered."
                )

            else:

                messages.success(
                    request,
                    f"{registered} unit(s) registered successfully."
                )

        else:

            messages.info(
                request,
                "The selected units are already registered."
            )

        return redirect(
            "semester_enrollment_detail",
            pk=enrollment.pk,
        )

    return render(
        request,
        "students/registrations/register_units.html",
        {
            "enrollment": enrollment,
            "units": available_units,
        },
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



    # Registration lock

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
    "students.view_semesterenrollment",
    raise_exception=True
)
def enrollment_list(request):

    enrollments = (
        SemesterEnrollment.objects
        .select_related(
            "student",
            "programme",
            "programme_level",
            "academic_year",
            "semester",
        )
        .order_by(
            "-academic_year",
            "-semester",
            "student__admission_no"
        )
    )


    # Search

    search = request.GET.get(
        "search"
    )

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


    programme = request.GET.get(
        "programme"
    )

    if programme:

        enrollments = enrollments.filter(
            programme_id=programme
        )


    programme_level = request.GET.get(
        "programme_level"
    )

    if programme_level:

        enrollments = enrollments.filter(
            programme_level_id=programme_level
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

        "programmes":
            Programme.objects.all(),

        "programme_levels":
            ProgrammeLevel.objects.all(),

        "statuses":
            SemesterEnrollment.STATUS_CHOICES,

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
            "enrollment_list"
        )


    if not active_semester:

        messages.error(
            request,
            "No active semester found."
        )

        return redirect(
            "enrollment_list"
        )


    if request.method == "POST":

        form = SemesterEnrollmentForm(
            request.POST
        )


        if form.is_valid():

            enrollment = form.save(
                commit=False
            )


            # Prevent duplicate enrollment

            exists = (
                SemesterEnrollment.objects
                .filter(
                    student=enrollment.student,
                    academic_year=active_year,
                    semester=active_semester
                )
                .exists()
            )


            if exists:

                messages.error(
                    request,
                    "Student already has an enrollment for this semester."
                )

                return redirect(
                    "enrollment_create"
                )


            # Automatically assign current academic period

            enrollment.academic_year = (
                active_year
            )

            enrollment.semester = (
                active_semester
            )


            # Ensure programme comes from student

            enrollment.programme = (
                enrollment.student.programme
            )


            # Automatically pick first programme level
            # (for new students)

            first_level = (
                ProgrammeLevel.objects
                .filter(
                    programme=enrollment.programme,
                    is_active=True
                )
                .order_by(
                    "progression_order"
                )
                .first()
            )


            if not first_level:

                messages.error(
                    request,
                    "No programme level configured for this programme."
                )

                return redirect(
                    "enrollment_create"
                )


            enrollment.programme_level = (
                first_level
            )


            enrollment.status = (
                SemesterEnrollment.ENROLLED
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
            "form": form,
            "active_year": active_year,
            "active_semester": active_semester,
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


    registrations = (
        enrollment.registrations
        .select_related(
            "unit",
            "unit__programme_level"
        )
    )


    return render(
        request,
        "students/enrollments/enrollment_detail.html",
        {
            "enrollment": enrollment,
            "registrations": registrations,
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

    q = request.GET.get("q")

    if q:
        applicants = applicants.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(application_no__icontains=q)
        )

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


    active_year = (
        AcademicYear.objects
        .filter(
            is_active=True
        )
        .first()
    )


    active_semester = (
        Semester.objects
        .filter(
            is_active=True
        )
        .first()
    )


    if not active_year:

        messages.error(
            request,
            "No active academic year configured."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )


    if not active_semester:

        messages.error(
            request,
            "No active semester configured."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )


    # First semester of the programme

    first_level = (
        ProgrammeLevel.objects
        .filter(
            programme=applicant.programme,
            is_active=True
        )
        .order_by(
            "progression_order"
        )
        .first()
    )


    if not first_level:

        messages.error(
            request,
            "Programme levels have not been configured."
        )

        return redirect(
            "applicant_detail",
            pk=applicant.pk
        )


    try:

        with transaction.atomic():


            student = Student.objects.create(

                first_name=applicant.first_name,

                middle_name=applicant.middle_name,

                last_name=applicant.last_name,

                gender=applicant.gender,

                date_of_birth=applicant.date_of_birth,

                id_number=applicant.id_number,

                phone=applicant.phone_number,

                email=applicant.email,

                address=applicant.address,

                programme=applicant.programme,

                admission_date=timezone.now().date(),

            )


            applicant.student = student

            applicant.status = "APPROVED"

            applicant.save()



            SemesterEnrollment.objects.create(

                student=student,

                programme=applicant.programme,

                programme_level=first_level,

                academic_year=active_year,

                semester=active_semester,

                status=SemesterEnrollment.ENROLLED,

            )


        messages.success(
            request,
            (
                "Applicant approved successfully. "
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

#Create Report View
@login_required
def admissions_report(request):

    by_intake = (
        Applicant.objects
        .values("intake__name")
        .annotate(total=Count("id"))
        .order_by("intake__name")
    )

    by_programme = (
        Applicant.objects
        .values("programme__programme_name")
        .annotate(total=Count("id"))
        .order_by("programme__programme_name")
    )

    by_department = (
        Applicant.objects
        .values("programme__department__department_name")
        .annotate(total=Count("id"))
        .order_by("programme__department__department_name")
    )

    context = {
        "by_intake": by_intake,
        "by_programme": by_programme,
        "by_department": by_department,
    }

    return render(
        request,
        "students/admissions_report.html",
        context,
    )
"""
@login_required
def lecturer_assignment_list(request):

    assignments = LecturerAssignment.objects.select_related(
        "lecturer",
        "unit",
        "academic_year",
        "semester"
    )

    return render(
        request,
        "students/assignments/assignment_list.html",
        {
            "assignments": assignments
        }
    )

@login_required
def lecturer_assignment_create(request):

    if request.method == "POST":

        form = LecturerAssignmentForm(request.POST)

        if form.is_valid():

            assignment = form.save(commit=False)

            assignment.assigned_by = request.user

            assignment.save()

            return redirect(
                "lecturer_assignment_list"
            )

    else:

        form = LecturerAssignmentForm()


    return render(
        request,
        "students/assignments/assignment_form.html",
        {
            "form": form
        }
    )

"""
@login_required
@permission_required(
    "students.view_lecturerassignment",
    raise_exception=True
)
def lecturer_assignment_list(request):

    assignments = LecturerAssignment.objects.select_related(
        "lecturer",
        "unit",
        "academic_year",
        "semester",
        "assigned_by",
    )

    return render(
        request,
        "students/assignments/assignment_list.html",
        {
            "assignments": assignments
        }
    )

@login_required
@permission_required(
    "students.add_lecturerassignment",
    raise_exception=True
)
def lecturer_assignment_create(request):

    if request.method == "POST":

        form = LecturerAssignmentForm(request.POST)

        if form.is_valid():

            assignment = form.save(commit=False)

            assignment.assigned_by = request.user

            assignment.save()

            return redirect(
                "lecturer_assignment_list"
            )

    else:

        form = LecturerAssignmentForm()

    return render(
        request,
        "students/assignments/assignment_form.html",
        {
            "form": form,
            "title": "Assign Unit to Lecturer",
        }
    )

@login_required
@permission_required(
    "students.change_lecturerassignment",
    raise_exception=True
)
def lecturer_assignment_update(request, pk):

    assignment = get_object_or_404(
        LecturerAssignment,
        pk=pk
    )

    if request.method == "POST":

        form = LecturerAssignmentForm(
            request.POST,
            instance=assignment
        )

        if form.is_valid():

            form.save()

            return redirect(
                "lecturer_assignment_list"
            )

    else:

        form = LecturerAssignmentForm(
            instance=assignment
        )

    return render(
        request,
        "students/assignments/assignment_form.html",
        {
            "form": form,
            "title": "Edit Lecturer Assignment",
        }
    )

@login_required
@permission_required(
    "students.delete_lecturerassignment",
    raise_exception=True
)
def lecturer_assignment_delete(request, pk):

    assignment = get_object_or_404(
        LecturerAssignment,
        pk=pk
    )

    if request.method == "POST":

        assignment.delete()

        return redirect(
            "lecturer_assignment_list"
        )

    return render(
        request,
        "students/assignments/assignment_confirm_delete.html",
        {
            "assignment": assignment
        }
    )

"""
@login_required
def my_units(request):

    assignments = LecturerAssignment.objects.select_related(
        "unit",
        "academic_year",
        "semester",
    ).filter(
        lecturer=request.user
    )

    return render(
        request,
        "students/exams/my_units.html",
        {
            "assignments": assignments
        }
    )"""

@login_required
def my_units(request):

    assignments = LecturerAssignment.objects.select_related(
        "unit",
        "academic_year",
        "semester",
    ).filter(
        lecturer=request.user
    )

    assignment_data = []

    for assignment in assignments:

        batch = ResultBatch.objects.filter(
            lecturer_assignment=assignment
        ).first()

        assignment_data.append(
            {
                "assignment": assignment,
                "batch": batch,
            }
        )

    return render(
        request,
        "students/exams/my_units.html",
        {
            "assignment_data": assignment_data,
        }
    )

@login_required
def enter_marks(request, assignment_id):

    assignment = get_object_or_404(
        LecturerAssignment,
        id=assignment_id,
        lecturer=request.user
    )

    batch = ResultBatch.objects.filter(
        lecturer_assignment=assignment
    ).first()

    locked = False

    if batch and batch.status in [
        "submitted",
        "approved"
    ]:
        locked = True

    registrations = Registration.objects.select_related(
        "enrollment__student"
    ).filter(
        unit=assignment.unit,
        enrollment__academic_year=assignment.academic_year,
        enrollment__semester=assignment.semester,
    )

    if locked:

        messages.error(
            request,
            "Results have already been submitted and cannot be edited."
        )

    elif request.method == "POST":

        for registration in registrations:

            cat1 = float(
                request.POST.get(
                    f"cat1_{registration.id}"
                ) or 0
            )

            cat2 = float(
                request.POST.get(
                    f"cat2_{registration.id}"
                ) or 0
            )

            exam = float(
                request.POST.get(
                    f"exam_{registration.id}"
                ) or 0
            )

            result, created = Result.objects.get_or_create(
                enrollment=registration.enrollment,
                unit=registration.unit,
            )

            result.cat1 = cat1
            result.cat2 = cat2
            result.exam = exam
            result.entered_by = request.user

            result.save()

        messages.success(
            request,
            "Marks saved successfully."
        )

    result_map = {}

    for registration in registrations:

        result_map[registration.id] = Result.objects.filter(
            enrollment=registration.enrollment,
            unit=registration.unit
        ).first()

    return render(
        request,
        "students/exams/enter_marks.html",
        {
            "assignment": assignment,
            "registrations": registrations,
            "result_map": result_map,
            "locked": locked,
        }
    )

@login_required
def unit_marksheet(request, assignment_id):

    assignment = get_object_or_404(
        LecturerAssignment,
        id=assignment_id
    )

    results = Result.objects.select_related(
        "enrollment__student"
    ).filter(
        unit=assignment.unit,
        enrollment__academic_year=assignment.academic_year,
        enrollment__semester=assignment.semester,
    ).order_by(
        "enrollment__student__admission_no"
    )

    status = "Draft"

    if results.exists():

        first_result = results.first()

        if first_result.is_approved:

            status = "Approved"

        elif first_result.is_submitted:

            status = "Submitted"

    return render(
        request,
        "students/exams/unit_marksheet.html",
        {
            "assignment": assignment,
            "results": results,
            "status": status,
        }
    )

@login_required
def export_marksheet_excel(request, assignment_id):

    from openpyxl import Workbook
    from openpyxl.styles import (
        Font,
        Alignment,
        Border,
        Side
    )
    from openpyxl.utils import get_column_letter

    assignment = get_object_or_404(
        LecturerAssignment,
        id=assignment_id
    )

    results = Result.objects.select_related(
        "enrollment__student"
    ).filter(
        unit=assignment.unit,
        enrollment__academic_year=assignment.academic_year,
        enrollment__semester=assignment.semester,
    ).order_by(
        "enrollment__student__admission_no"
    )

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Marksheet"

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    # ==================================================
    # HEADER
    # ==================================================

    sheet.merge_cells("A1:H1")
    sheet["A1"] = (
        "SANFIELDS INSTITUTE OF BUSINESS & TECHNOLOGY"
    )

    sheet["A1"].font = Font(
        bold=True,
        size=16
    )

    sheet["A1"].alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    sheet.merge_cells("A2:H2")

    sheet["A2"] = (
        "OFFICIAL UNIT MARKSHEET"
    )

    sheet["A2"].font = Font(
        bold=True,
        size=12
    )

    sheet["A2"].alignment = Alignment(
        horizontal="center",
        vertical="center"
    )

    sheet["A4"] = "Unit"
    sheet["B4"] = str(
        assignment.unit
    )

    sheet["E4"] = "Programme"
    sheet["F4"] = str(
        assignment.unit.course.programme
    )

    sheet["A5"] = "Department"
    sheet["B5"] = str(
        assignment.unit.course.programme.department
    )

    sheet["E5"] = "Academic Year"
    sheet["F5"] = str(
        assignment.academic_year
    )

    sheet["A6"] = "Semester"
    sheet["B6"] = str(
        assignment.semester
    )

    sheet["E6"] = "Lecturer"
    sheet["F6"] = (
        assignment.lecturer.get_full_name()
        or assignment.lecturer.username
    )

    # ==================================================
    # TABLE HEADERS
    # ==================================================

    headers = [
        "Admission No",
        "Student Name",
        "CAT 1",
        "CAT 2",
        "Exam",
        "Total",
        "Grade",
        "Remarks",
    ]

    header_row = 8

    for col_num, header in enumerate(
        headers,
        start=1
    ):

        cell = sheet.cell(
            row=header_row,
            column=col_num
        )

        cell.value = header

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

        cell.border = thin_border

    # ==================================================
    # RESULTS
    # ==================================================

    row_num = 9

    for result in results:

        sheet.cell(
            row=row_num,
            column=1
        ).value = (
            result.enrollment.student.admission_no
        )

        sheet.cell(
            row=row_num,
            column=2
        ).value = str(
            result.enrollment.student
        )

        sheet.cell(
            row=row_num,
            column=3
        ).value = result.cat1

        sheet.cell(
            row=row_num,
            column=4
        ).value = result.cat2

        sheet.cell(
            row=row_num,
            column=5
        ).value = result.exam

        sheet.cell(
            row=row_num,
            column=6
        ).value = result.total

        sheet.cell(
            row=row_num,
            column=7
        ).value = result.grade

        sheet.cell(
            row=row_num,
            column=8
        ).value = result.remarks

        for col in range(1, 9):

            current_cell = sheet.cell(
                row=row_num,
                column=col
            )

            current_cell.border = thin_border

            current_cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

        row_num += 1

    # ==================================================
    # ROW HEIGHTS
    # ==================================================

    for row in range(
        8,
        sheet.max_row + 1
    ):

        sheet.row_dimensions[
            row
        ].height = 25

    # ==================================================
    # COLUMN WIDTHS
    # ==================================================

    for col in range(1, 9):

        max_length = 0

        column_letter = get_column_letter(
            col
        )

        for row in range(
            1,
            sheet.max_row + 1
        ):

            cell = sheet.cell(
                row=row,
                column=col
            )

            if cell.value:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        sheet.column_dimensions[
            column_letter
        ].width = max_length + 5

    sheet.column_dimensions["B"].width = 35
    sheet.column_dimensions["H"].width = 20

    # ==================================================
    # SIGNATURES
    # ==================================================

    row_num += 3

    sheet.cell(
        row=row_num,
        column=1
    ).value = "Lecturer Signature"

    sheet.cell(
        row=row_num,
        column=4
    ).value = "HOD Signature"

    sheet.cell(
        row=row_num,
        column=7
    ).value = "Exam Officer Signature"

    # ==================================================
    # DOWNLOAD
    # ==================================================

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

    filename = (
        f"{assignment.unit.unit_code}_marksheet.xlsx"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="{filename}"'
    )

    workbook.save(response)

    return response


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone


@login_required
def submit_results(request, assignment_id):

    assignment = get_object_or_404(
        LecturerAssignment,
        id=assignment_id,
        lecturer=request.user
    )

    batch, created = ResultBatch.objects.get_or_create(
        lecturer_assignment=assignment,
        defaults={
            "unit": assignment.unit,
            "academic_year": assignment.academic_year,
            "semester": assignment.semester,
        }
    )

    # Prevent duplicate submission
    if batch.status == "submitted":
        messages.warning(
            request,
            "Results have already been submitted."
        )

        return redirect(
            "enter_marks",
            assignment_id=assignment.id
        )

    # Prevent submission after approval
    if batch.status == "approved":
        messages.error(
            request,
            "Results have already been approved."
        )

        return redirect(
            "enter_marks",
            assignment_id=assignment.id
        )

    results = Result.objects.filter(
        enrollment__academic_year=assignment.academic_year,
        enrollment__semester=assignment.semester,
        unit=assignment.unit,
        batch__isnull=True,
    )

    if not results.exists():
        messages.error(
            request,
            "No results available for submission."
        )

        return redirect(
            "enter_marks",
            assignment_id=assignment.id
        )

    results.update(
        batch=batch,
        is_submitted=True,
        submitted_at=timezone.now()
    )

    batch.status = "submitted"
    batch.submitted_by = request.user
    batch.submitted_at = timezone.now()
    batch.save()

    messages.success(
        request,
        "Results submitted successfully."
    )

    return redirect("my_units")


@login_required
@permission_required(
    "students.view_resultbatch",
    raise_exception=True
)
def approval_queue(request):

    batches = ResultBatch.objects.select_related(
        "unit",
        "academic_year",
        "semester",
        "submitted_by",
    ).exclude(
        status="draft"
    )
    return render(
        request,
        "students/exams/approval_queue.html",
        {
            "batches": batches
        }
    )


@login_required
@permission_required(
    "students.change_resultbatch",
    raise_exception=True
)
def approve_results(request, batch_id):

    batch = get_object_or_404(
        ResultBatch,
        id=batch_id
    )

    # Prevent approving already approved batches

    if batch.status == "approved":

        messages.warning(
            request,
            "This result batch is already approved."
        )

        return redirect(
            "approval_queue"
        )


    # Only submitted batches should be approved

    if batch.status != "submitted":

        messages.error(
            request,
            "Only submitted result batches can be approved."
        )

        return redirect(
            "approval_queue"
        )


    batch.status = "approved"

    batch.approved_by = request.user

    batch.approved_at = timezone.now()

    batch.save()


    messages.success(
        request,
        "Results approved successfully."
    )


    return redirect(
        "approval_queue"
    )


@login_required
@permission_required(
    "students.change_resultbatch",
    raise_exception=True
)
def return_results(request, batch_id):

    batch = get_object_or_404(
        ResultBatch,
        id=batch_id
    )

    if request.method == "POST":

        remarks = request.POST.get(
            "remarks"
        )

        if not remarks:

            messages.error(
                request,
                "Please provide a reason for returning results."
            )

            return render(
                request,
                "students/exams/return_results.html",
                {
                    "batch": batch
                }
            )

        batch.status = "returned"

        batch.remarks = remarks

        batch.save()

        messages.success(
            request,
            "Results returned for correction."
        )

        return redirect(
            "approval_queue"
        )


    return render(
        request,
        "students/exams/return_results.html",
        {
            "batch": batch
        }
    )


@login_required
@permission_required(
    "students.view_resultbatch",
    raise_exception=True
)
def view_batch(request, batch_id):

    batch = get_object_or_404(
        ResultBatch,
        id=batch_id
    )

    results = Result.objects.select_related(
        "enrollment__student"
    ).filter(
        batch=batch
    )

    return render(
        request,
        "students/exams/view_batch.html",
        {
            "batch": batch,
            "results": results,
        }
    )

@login_required
@permission_required(
    "students.view_resultbatch",
    raise_exception=True
)
def batch_details(request, batch_id):

    batch = get_object_or_404(
        ResultBatch.objects.select_related(
            "unit",
            "academic_year",
            "semester",
            "submitted_by",
            "approved_by",
        ),
        id=batch_id
    )

    results = Result.objects.select_related(
        "enrollment__student"
    ).filter(
        batch=batch
    ).order_by(
        "enrollment__student__admission_no"
    )

    return render(
        request,
        "students/exams/batch_details.html",
        {
            "batch": batch,
            "results": results,
        }
    )


@login_required
@permission_required(
    "students.change_resultbatch",
    raise_exception=True
)
def unlock_batch(request, batch_id):

    batch = get_object_or_404(
        ResultBatch,
        id=batch_id
    )


    if request.method == "POST":

        remarks = request.POST.get(
            "remarks"
        )


        if not remarks:

            messages.error(
                request,
                "Unlock reason is required."
            )

            return render(
                request,
                "students/exams/unlock_batch.html",
                {
                    "batch": batch
                }
            )


        batch.status = "unlocked"

        batch.remarks = remarks

        batch.save()


        ResultBatchLog.objects.create(
            batch=batch,
            action="Unlocked",
            performed_by=request.user,
            remarks=remarks,
        )


        messages.success(
            request,
            "Result batch unlocked successfully."
        )


        return redirect(
            "approval_queue"
        )


    return render(
        request,
        "students/exams/unlock_batch.html",
        {
            "batch": batch
        }
    )

#student portal
@login_required
def student_results(request):

    student = get_object_or_404(
        Student,
        user=request.user
    )


    results = Result.objects.select_related(
        "batch",
        "unit",
        "enrollment__student"
    ).filter(
        enrollment__student=student,
        batch__status="approved"
    ).order_by(
        "unit__code"
    )


    return render(
        request,
        "students/results/student_results.html",
        {
            "student": student,
            "results": results,
        }
    )


@login_required
def enrollment_results(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment.objects.select_related(
            "student",
            "programme_level__programme",
            "academic_year",
            "semester",
        ),
        pk=pk,
    )

    results = (
        Result.objects.filter(
            enrollment=enrollment,
        )
        .select_related("unit", "batch")
        .order_by("unit__code")
    )

    return render(
        request,
        "students/results/enrollment_results.html",
        {
            "enrollment": enrollment,
            "student": enrollment.student,
            "results": results,
        },
    )


@login_required
@permission_required(
    "students.change_semesterenrollment",
    raise_exception=True
)
def progress_student(request, enrollment_id):

    current_enrollment = get_object_or_404(
        SemesterEnrollment,
        id=enrollment_id
    )


    current_level = (
        current_enrollment.programme_level
    )


    next_level = (
        ProgrammeLevel.objects
        .filter(
            programme=current_enrollment.programme,
            progression_order__gt=
            current_level.progression_order,
            is_active=True
        )
        .order_by(
            "progression_order"
        )
        .first()
    )


    if not next_level:

        messages.warning(
            request,
            "Student has reached the final programme level."
        )

        return redirect(
            "enrollment_list"
        )

    # Find next semester

    next_semester = (
        Semester.objects
        .filter(
            academic_year=
            current_enrollment.academic_year,
            semester_name__icontains=
            "Semester"
        )
        .first()
    )


    if not next_semester:

        messages.error(
            request,
            "Next semester configuration missing."
        )

        return redirect(
            "enrollment_list"
        )



    try:

        with transaction.atomic():


            current_enrollment.status = (
                SemesterEnrollment.PROGRESSED
            )

            current_enrollment.save()



            new_enrollment = (
                SemesterEnrollment.objects.create(

                    student=
                    current_enrollment.student,

                    programme=
                    current_enrollment.programme,

                    programme_level=
                    next_level,

                    academic_year=
                    current_enrollment.academic_year,

                    semester=
                    next_semester,

                    status=
                    SemesterEnrollment.ENROLLED,

                )
            )


        messages.success(
            request,
            (
                f"Student progressed to "
                f"{next_level.name}"
            )
        )


    except Exception as e:

        messages.error(
            request,
            f"Progression failed: {e}"
        )


    return redirect(
        "enrollment_list"
    )


@login_required
@permission_required(
    "students.view_semesterenrollment",
    raise_exception=True
)
def progression_list(request):

    enrollments = (
        SemesterEnrollment.objects
        .filter(
            status=SemesterEnrollment.ENROLLED
        )
        .select_related(
            "student",
            "programme",
            "programme_level",
            "academic_year",
            "semester",
        )
        .order_by(
            "programme",
            "programme_level__progression_order",
            "student__admission_no"
        )
    )


    progression_data = []


    for enrollment in enrollments:


        next_level = (
            ProgrammeLevel.objects
            .filter(
                programme=enrollment.programme,
                progression_order__gt=
                enrollment.programme_level.progression_order,
                is_active=True
            )
            .order_by(
                "progression_order"
            )
            .first()
        )


        progression_data.append(
            {
                "enrollment": enrollment,

                "next_level": next_level
            }
        )


    return render(
        request,
        "students/progression/progression_list.html",
        {
            "progression_data":
            progression_data
        }
    )


@login_required
@permission_required(
    "students.view_programmelevel",
    raise_exception=True
)
def programme_level_list(request):

    programme_levels = (
        ProgrammeLevel.objects
        .select_related(
            "programme",
            "programme__course",
            "programme__course__department",
        )
        .order_by(
            "programme__name",
            "progression_order",
        )
    )

    context = {
        "programme_levels": programme_levels
    }

    return render(
        request,
        "students/programme_levels/programme_level_list.html",
        context
    )

@login_required
@permission_required(
    "students.add_programmelevel",
    raise_exception=True
)
def programme_level_create(request):

    if request.method == "POST":

        form = ProgrammeLevelForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Programme Level created successfully."
            )

            return redirect(
                "programme_level_list"
            )

    else:

        form = ProgrammeLevelForm()


    return render(
        request,
        "students/programme_levels/programme_level_form.html",
        {
            "form": form
        }
    )


@login_required
@permission_required(
    "students.change_programmelevel",
    raise_exception=True
)
def programme_level_update(request, pk):

    level = get_object_or_404(
        ProgrammeLevel,
        pk=pk
    )


    if request.method == "POST":

        form = ProgrammeLevelForm(
            request.POST,
            instance=level
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Programme Level updated successfully."
            )

            return redirect(
                "programme_level_list"
            )


    else:

        form = ProgrammeLevelForm(
            instance=level
        )


    return render(
        request,
        "students/programme_levels/programme_level_form.html",
        {
            "form": form,
            "level": level,
        }
    )

@login_required
@permission_required(
    "students.delete_programmelevel",
    raise_exception=True
)
def programme_level_delete(request, pk):

    level = get_object_or_404(
        ProgrammeLevel,
        pk=pk
    )


    if request.method == "POST":

        level.delete()

        messages.success(
            request,
            "Programme Level deleted"
        )

        return redirect(
            "programme_level_list"
        )


    return render(
        request,
        "students/programme_levels/programme_level_confirm_delete.html",
        {
            "level": level
        }
    )


@login_required
def load_programme_levels(request):

    programme_id = request.GET.get(
        "programme_id"
    )


    levels = ProgrammeLevel.objects.filter(
        programme_id=programme_id
    ).order_by(
        "progression_order"
    )


    return JsonResponse(
        list(
            levels.values(
                "id",
                "name"
            )
        ),
        safe=False
    )

@login_required
def programme_level_units(request, pk):

    programme_level = get_object_or_404(
        ProgrammeLevel,
        pk=pk
    )

    units = programme_level.units.filter(
        is_active=True
    )

    context = {
        "programme_level": programme_level,
        "units": units,
    }

    return render(
        request,
        "students/programme_levels/programme_level_units.html",
        context
    )


def add_programme_level_unit(request, pk):

    programme_level = get_object_or_404(
        ProgrammeLevel,
        pk=pk
    )

    if request.method == "POST":

        code = request.POST.get("code")
        name = request.POST.get("name")
        credit_hours = request.POST.get("credit_hours")


        Unit.objects.create(

            programme_level=programme_level,

            code=code,

            name=name,

            credit_hours=credit_hours

        )


        return redirect(
            "programme_level_units",
            pk=programme_level.id
        )


    context = {
        "programme_level": programme_level
    }


    return render(
        request,
        "students/programme_levels/add_unit.html",
        context
    )

def semester_enrollment_list(request):

    enrollments = SemesterEnrollment.objects.select_related(
        "student",
        "programme",
        "programme_level",
        "academic_year",
        "semester",
    )

    return render(
        request,
        "students/enrollments/enrollment_list.html",
        {
            "enrollments": enrollments
        }
    )

@transaction.atomic
def semester_enrollment_create(request):

    form = SemesterEnrollmentForm(
        request.POST or None
    )


    if form.is_valid():


        enrollment = form.save()



        try:

            generate_student_invoice(
                enrollment
            )


            update_financial_clearance(
                enrollment,
                request.user
            )


            messages.success(

                request,

                "Semester enrollment created and invoice generated successfully."

            )


        except ValueError as e:


            messages.warning(

                request,

                str(e)

            )



        return redirect(

            "semester_enrollment_detail",

            pk=enrollment.pk

        )



    return render(

        request,

        "students/enrollments/enrollment_form.html",

        {

            "form": form

        }

    )


def semester_enrollment_detail(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )

    registrations = enrollment.registrations.all()


    return render(
        request,
        "students/enrollments/enrollment_detail.html",
        {
            "enrollment": enrollment,
            "registrations": registrations
        }
    )

def semester_enrollment_edit(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )


    form = SemesterEnrollmentForm(
        request.POST or None,
        instance=enrollment
    )


    if form.is_valid():

        form.save()

        return redirect(
            "semester_enrollment_list"
        )


    return render(
        request,
        "students/enrollments/enrollment_form.html",
        {
            "form":form
        }
    )


def semester_enrollment_delete(request, pk):

    enrollment = get_object_or_404(
        SemesterEnrollment,
        pk=pk
    )


    if request.method == "POST":

        enrollment.delete()

        return redirect(
            "semester_enrollment_list"
        )


    return render(
        request,
        "students/enrollments/enrollment_confirm_delete.html",
        {
            "enrollment": enrollment
        }
    )


@login_required
@transaction.atomic
def enroll_student(request, pk):
    student = get_object_or_404(
        Student.objects.select_related(
            "programme"
        ),
        pk=pk

    )
    academic_year = AcademicYear.objects.filter(

        is_active=True

    ).first()

    if not academic_year:
        messages.error(

            request,
            "There is no active academic year."
        )
        return redirect(

            "student_detail",

            id=student.pk

        )

    semester = Semester.objects.filter(
        is_active=True

    ).first()

    if not semester:
        messages.error(
            request,
            "There is no active semester."
        )
        return redirect(

            "student_detail",

            id=student.pk

        )
    programme_level = ProgrammeLevel.objects.filter(

        programme=student.programme,

        is_active=True,

    ).order_by(

        "progression_order"

    ).first()

    if not programme_level:
        messages.error(
            request,

            "No active programme level found."
        )
        return redirect(

            "student_detail",

            id=student.pk

        )
    enrollment, created = SemesterEnrollment.objects.get_or_create(
        student=student,
        academic_year=academic_year,
        semester=semester,
        defaults={
            "programme": student.programme,

            "programme_level": programme_level,

            "status": SemesterEnrollment.ENROLLED,
        }
    )

    if created:
        try:
            generate_student_invoice(
                enrollment
            )

            update_financial_clearance(
                enrollment,
                request.user
            )

            messages.success(
                request,
                "Student enrolled and invoice generated successfully."
            )

        except ValueError as e:
            messages.warning(
                request,
                str(e)

            )

    else:
        messages.info(
            request,
            "Student is already enrolled for the active semester."
        )
    return redirect(
        "semester_enrollment_detail",
        pk=enrollment.pk

    )

class StudentDeleteView(DeleteView):

    model = Student

    template_name = "students/students/student_delete.html"

    context_object_name = "student"

    success_url = reverse_lazy("student_list")

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        if self.object.enrollments.exists():

            messages.error(

                request,

                (
                    "This student cannot be deleted because "
                    "semester enrollment records exist."
                ),

            )

            return redirect(

                "student_detail",

                self.object.pk,

            )

        return super().post(request, *args, **kwargs)