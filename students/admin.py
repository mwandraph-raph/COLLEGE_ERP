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
from .models import Programme, Student, Department 

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


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "admission_no",
        "first_name",
        "last_name",
        "programme",
        "phone",
    )

    search_fields = (
        "admission_no",
        "first_name",
        "last_name",
    )

    list_filter = (
        "programme",
    )

    ordering = (
        "admission_no",
    )

    list_per_page = 20



