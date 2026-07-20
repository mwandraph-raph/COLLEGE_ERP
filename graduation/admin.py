from django.contrib import admin
from .models import Graduation

# Register your models here.

@admin.register(Graduation)
class GraduationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "academic_year",
        "status",
        "certificate_number",
        "graduation_date",
    )

    list_filter = (
        "status",
        "academic_year",
    )

    search_fields = (
        "student__admission_no",
        "student__first_name",
        "student__last_name",
        "certificate_number",
    )