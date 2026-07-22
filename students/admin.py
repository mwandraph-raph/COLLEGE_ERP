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
admin.site.register(Department)
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