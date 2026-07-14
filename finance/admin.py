from django.contrib import admin
from .models import (
    FeeCategory,
)
# Register your models here.
@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    list_filter = (
        "is_active",
    )