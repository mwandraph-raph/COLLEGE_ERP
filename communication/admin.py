from django.contrib import admin

from .models import (
    AcademicEvent,
    Announcement,
    AnnouncementRead,
    StudentFeedbackForm,
)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "is_important", "is_published", "published_at", "created_by")
    list_filter = ("audience", "is_important", "is_published")
    search_fields = ("title", "body")


@admin.register(AcademicEvent)
class AcademicEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "audience", "start_at", "is_published", "created_by")
    list_filter = ("event_type", "audience", "is_published", "is_important")
    search_fields = ("title", "description")


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ("announcement", "student", "read_at")
    search_fields = ("announcement__title", "student__admission_no", "student__first_name", "student__last_name")
    readonly_fields = ("announcement", "student", "read_at")


@admin.register(StudentFeedbackForm)
class StudentFeedbackFormAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "audience",
        "is_published",
        "starts_at",
        "closes_at",
        "created_by",
    )

    list_filter = (
        "audience",
        "is_published",
    )

    search_fields = (
        "title",
        "description",
        "google_form_url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Google Form",
            {
                "fields": (
                    "title",
                    "description",
                    "google_form_url",
                )
            },
        ),
        (
            "Audience",
            {
                "fields": (
                    "audience",
                    "department",
                    "programme",
                    "student",
                )
            },
        ),
        (
            "Publication",
            {
                "fields": (
                    "is_published",
                    "published_at",
                    "starts_at",
                    "closes_at",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )