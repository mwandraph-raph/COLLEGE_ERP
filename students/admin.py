"""from django.contrib import admin

# Register your models here.
from .models import (
    Programme,
    Student,
)
admin.site.register(Programme)
admin.site.register(Student)
"""
from django.contrib import admin
from .models import (Programme, 
                     Student, 
                     Department,
                     AcademicYear, 
                     Semester, 
                     Course, 
                     Unit, 
                     Registration,
                     StudyLevel,
                     SemesterEnrollment,
                     Applicant,
                     )

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "programme",
        "status",
        "application_date",
    )

    list_filter = (
        "status",
        "programme",
    )

    search_fields = (
        "first_name",
        "last_name",
        "id_number",
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "department_name",
    )


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        "programme_name",
        "department",
    )
    
    search_fields = (
        "programme_name",
    )

    list_filter = (
        "department",
    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "year_name",
        "is_active",
    )

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):

    list_display = (
        "semester_name",
        "academic_year",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "is_active",
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "course_code",
        "course_name",
        "programme",
        "semester",
        "credit_hours",
    )

    search_fields = (
        "course_code",
        "course_name",
    )

    list_filter = (
        "programme",
        "semester",
    )

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):

    list_display = (
        "unit_code",
        "unit_name",
        "course",
        "credit_hours",
    )

    search_fields = (
        "unit_code",
        "unit_name",
    )

    list_filter = (
        "course",
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "admission_no",
        "first_name",
        "last_name",
        "programme",
        "user",
    )

    search_fields = (
        "admission_no",
        "first_name",
        "last_name",
    )

@admin.register(SemesterEnrollment)
class SemesterEnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "academic_year",
        "semester",
        "study_level",
        "status",
    )

    list_filter = (
        "academic_year",
        "semester",
        "status",
    )

    search_fields = (
        "student__admission_no",
        "student__first_name",
        "student__last_name",
    )

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "enrollment",
        "unit",
        "registration_date",
    )

    list_filter = (
        "enrollment__academic_year",
        "enrollment__semester",
    )

    search_fields = (
        "enrollment__student__admission_no",
        "enrollment__student__first_name",
        "enrollment__student__last_name",
        "unit__unit_code",
        "unit__unit_name",
    )

@admin.register(StudyLevel)
class StudyLevelAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "level_name",
    )

    search_fields = (
        "level_name",
    )