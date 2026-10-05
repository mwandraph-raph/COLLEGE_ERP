from django.contrib import admin

from .models import (
    Applicant,
    Department,
    Course,
    Programme,
    ProgrammeLevel,
    AcademicYear,
    Intake,
    Semester,
    Unit,
)


admin.site.register(Applicant)
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "hod",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "hod__username",
        "hod__first_name",
        "hod__last_name",
    )

admin.site.register(Course)
admin.site.register(Programme)
admin.site.register(ProgrammeLevel)

admin.site.register(Intake)
admin.site.register(Semester)
admin.site.register(Unit)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "year_name",
        "is_active",
        "registration_open",
    )

    list_filter = (
        "is_active",
        "registration_open",
    )