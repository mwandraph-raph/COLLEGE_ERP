from django.contrib import admin
from django.utils.html import format_html

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):

    list_display = (
        "created_at",
        "user",
        "module_badge",
        "action_badge",
        "severity_badge",
        "object_name",
        "ip_address",
    )

    list_filter = (
        "module",
        "action",
        "severity",
        "created_at",
    )

    search_fields = (
        "description",
        "object_name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = (
        "created_at",
        "user",
        "module",
        "action",
        "severity",
        "description",
        "object_id",
        "object_name",
        "ip_address",
        "user_agent",
    )

    ordering = ("-created_at",)

    list_per_page = 50

    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="Module")
    def module_badge(self, obj):

        colors = {
            "Admissions": "#2563eb",
            "Students": "#7c3aed",
            "Registration": "#0f766e",
            "Enrollment": "#0891b2",
            "Finance": "#16a34a",
            "Academics": "#ea580c",
            "Transcript": "#9333ea",
            "Graduation": "#dc2626",
            "System": "#334155",
        }

        color = colors.get(obj.module, "#6b7280")

        return format_html(
            '<span style="background:{};color:white;padding:5px 12px;border-radius:30px;font-weight:600;">{}</span>',
            color,
            obj.module,
        )

    @admin.display(description="Action")
    def action_badge(self, obj):

        colors = {
            "Create": "#16a34a",
            "Update": "#2563eb",
            "Delete": "#dc2626",
            "Approve": "#059669",
            "Reject": "#d97706",
            "Generate": "#7c3aed",
            "Print": "#0f766e",
            "Login": "#0284c7",
            "Logout": "#64748b",
        }

        color = colors.get(obj.action, "#6b7280")

        return format_html(
            '<span style="background:{};color:white;padding:5px 12px;border-radius:30px;font-weight:600;">{}</span>',
            color,
            obj.action,
        )

    @admin.display(description="Severity")
    def severity_badge(self, obj):

        colors = {
            "Info": "#16a34a",
            "Warning": "#f59e0b",
            "Critical": "#dc2626",
        }

        color = colors.get(obj.severity, "#6b7280")

        return format_html(
            '<span style="background:{};color:white;padding:5px 12px;border-radius:30px;font-weight:600;">{}</span>',
            color,
            obj.severity,
        )