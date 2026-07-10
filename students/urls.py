from django.urls import path
from . import views
from students.views import (
     semester_list,
    semester_create,
    semester_update,
    semester_delete,
    activate_semester,
)

urlpatterns = [

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "students/",
        views.student_list,
        name="student_list",
    ),

    path(
        "students/create/",
        views.student_create,
        name="student_create",
    ),

    path(
        "students/<int:id>/",
        views.student_detail,
        name="student_detail",
    ),

    path(
        "students/<int:id>/edit/",
        views.student_update,
        name="student_update",
    ),

    path(
    "students/<int:id>/delete/",
    views.student_delete,
    name="student_delete",
    ),

    path(
        "departments/",
        views.department_list,
        name="department_list"
    ),

    path(
        "departments/create/",
        views.department_create,
        name="department_create"
    ),

    path(
        "departments/<int:pk>/update/",
        views.department_update,
        name="department_update"
    ),

    path(
        "departments/<int:pk>/delete/",
        views.department_delete,
        name="department_delete"
    ),

    path(
    "programmes/",
    views.programme_list,
    name="programme_list"
),

path(
    "programmes/create/",
    views.programme_create,
    name="programme_create"
),

path(
    "programmes/<int:pk>/update/",
    views.programme_update,
    name="programme_update"
),

path(
    "programmes/<int:pk>/delete/",
    views.programme_delete,
    name="programme_delete"
),

path(
    "academic-years/",
    views.academic_year_list,
    name="academic_year_list"
),

path(
    "academic-years/create/",
    views.academic_year_create,
    name="academic_year_create"
),

path(
    "academic-years/<int:pk>/edit/",
    views.academic_year_update,
    name="academic_year_update"
),

path(
    "academic-years/<int:pk>/delete/",
    views.academic_year_delete,
    name="academic_year_delete"
),

path(
    "academic-years/<int:pk>/open/",
    views.open_registration,
    name="open_registration"
),

path(
    "academic-years/<int:pk>/close/",
    views.close_registration,
    name="close_registration"
),

path(
    "semesters/",
    semester_list,
    name="semester_list"
),

path(
    "semesters/create/",
    semester_create,
    name="semester_create"
),

path(
    "semesters/<int:pk>/edit/",
    semester_update,
    name="semester_update"
),

path(
    "semesters/<int:pk>/delete/",
    semester_delete,
    name="semester_delete"
),

path(
    "semesters/<int:pk>/activate/",
    activate_semester,
    name="activate_semester"
),

path(
    "courses/",
    views.course_list,
    name="course_list"
),

path(
    "courses/create/",
    views.course_create,
    name="course_create"
),

path(
    "courses/<int:pk>/update/",
    views.course_update,
    name="course_update"
),

path(
    "courses/<int:pk>/delete/",
    views.course_delete,
    name="course_delete"
),

path(
    "units/",
    views.unit_list,
    name="unit_list"
),

path(
    "units/create/",
    views.unit_create,
    name="unit_create"
),

path(
    "units/<int:pk>/update/",
    views.unit_update,
    name="unit_update"
),

path(
    "units/<int:pk>/delete/",
    views.unit_delete,
    name="unit_delete"
),

# Registration Management

path(
    "registrations/",
    views.registration_list,
    name="registration_list"
),

path(
    "registrations/create/",
    views.registration_create,
    name="registration_create"
),

path(
    "registrations/<int:pk>/update/",
    views.registration_update,
    name="registration_update"
),

path(
    "registrations/<int:pk>/delete/",
    views.registration_delete,
    name="registration_delete"
),

path(
    "my-registrations/",
    views.my_registrations,
    name="my_registrations"
),

path(
    "register-units/",
    views.register_units,
    name="register_units"
),

path(
    "registrations/<int:pk>/drop/",
    views.drop_registration,
    name="drop_registration"
),

path(
    "study-levels/",
    views.study_level_list,
    name="study_level_list"
),

path(
    "study-levels/add/",
    views.study_level_create,
    name="study_level_create"
),

path(
    "study-levels/<int:pk>/edit/",
    views.study_level_update,
    name="study_level_update"
),

path(
    "study-levels/<int:pk>/delete/",
    views.study_level_delete,
    name="study_level_delete"
),

path(
    "enrollments/",
    views.enrollment_list,
    name="enrollment_list"
),

path(
    "enrollments/create/",
    views.enrollment_create,
    name="enrollment_create"
),

path(
    "enrollments/<int:pk>/",
    views.enrollment_detail,
    name="enrollment_detail"
),

path(
    "enrollments/<int:pk>/edit/",
    views.enrollment_update,
    name="enrollment_update"
),

path(
    "enrollments/<int:pk>/delete/",
    views.enrollment_delete,
    name="enrollment_delete"
),

path(
    "applicants/",
    views.applicant_list,
    name="applicant_list",
),

path(
    "applicants/add/",
    views.applicant_create,
    name="applicant_create",
),

path(
    "applicants/<int:pk>/",
    views.applicant_detail,
    name="applicant_detail"
),

path(
    "applicants/<int:pk>/edit/",
    views.applicant_update,
    name="applicant_update",
),

path(
    "applicants/<int:pk>/delete/",
    views.applicant_delete,
    name="applicant_delete",
),

path(
    "applicants/<int:pk>/approve/",
    views.approve_applicant,
    name="approve_applicant",
),

path(
    "intakes/",
    views.intake_list,
    name="intake_list"
),

path(
    "intakes/add/",
    views.intake_create,
    name="intake_create"
),

path(
    "intakes/<int:pk>/edit/",
    views.intake_update,
    name="intake_update"
),

path(
    "intakes/<int:pk>/delete/",
    views.intake_delete,
    name="intake_delete"
),

path(
    "admissions-report/",
    views.admissions_report,
    name="admissions_report",
),
]